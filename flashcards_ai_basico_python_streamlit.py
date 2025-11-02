# app.py — Flashcards AI básico con Streamlit (un solo archivo)
# Características:
# - Crear/editar/borrar tarjetas (frente, reverso, notas)
# - Búsqueda "semántica" simple (tokens + coseno)
# - Planificación SM-2 simplificada (spaced repetition)
# - Etiquetado automático heurístico por palabras clave
# - Importar/Exportar TSV (Frente \t Reverso \t Notas)
# - Persistencia en disco (cards.json)
# - Interfaz en español, sin dependencias de IA externas (opcional ampliar con API luego)

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import streamlit as st

APP_TITLE = "Flashcards AI básico (Python + Streamlit)"
STORAGE_FILE = "cards.json"

# ----------------------- Utilidades de texto -----------------------
SPANISH_STOPWORDS = set(
    "a,ante,bajo,cabe,con,contra,de,desde,en,entre,hacia,hasta,para,por,segun,sin,sobre,tras,un,una,unos,unas,el,la,los,las,lo,y,o,u,que,como,del,al,es,son,ser,estar,esta,este,estos,estas,ese,esa,eso,esas,esos"
    .split(",")
)

import unicodedata

def _strip_accents(s: str) -> str:
    """Elimina diacríticos usando unicodedata (sin dependencias externas).
    Descompone en NFD y filtra los caracteres de categoría 'Mn' (marcas combinantes).
    """
    decomposed = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def tokenize(text: str) -> List[str]:
    t = (
        _strip_accents(text.lower())
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    toks = [w for w in t.split() if w and w not in SPANISH_STOPWORDS and len(w) > 2]
    return toks


def build_vocab(docs: List[str]):
    vocab: Dict[str, int] = {}
    for d in docs:
        for tok in tokenize(d):
            if tok not in vocab:
                vocab[tok] = len(vocab)
    return vocab


def vectorize(text: str, vocab: Dict[str, int]) -> np.ndarray:
    vec = np.zeros(len(vocab), dtype=float)
    for tok in tokenize(text):
        if tok in vocab:
            vec[vocab[tok]] += 1.0
    # tf-normalization opcional
    return vec


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ----------------------- SM-2 simplificado -----------------------
# Referencia: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2

def schedule(card: Dict[str, Any], quality: int) -> Dict[str, Any]:
    # card: { ef, reps, interval_days, due }
    ef = float(card.get("ef", 2.5))
    reps = int(card.get("reps", 0))
    interval_days = int(card.get("interval_days", 0))

    if quality < 3:
        reps = 0
        interval_days = 1
    else:
        if reps == 0:
            interval_days = 1
        elif reps == 1:
            interval_days = 6
        else:
            interval_days = int(round(interval_days * ef))
        reps += 1

    ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    due = datetime.utcnow() + timedelta(days=interval_days)

    card.update(
        {
            "ef": ef,
            "reps": reps,
            "interval_days": interval_days,
            "due": due.isoformat(),
        }
    )
    return card


# ----------------------- Etiquetado heurístico -----------------------
DEFAULT_TAGS = {
    r"ecg|electro": "Cardiología",
    r"renal|creatin|tfga|kdigo": "Nefrología",
    r"asm|epoc|bronco|gold": "Neumología",
    r"sepsis|sofa|qsofa|lactato": "Cuidados Críticos",
    r"hepat|bilirr|alt|ast|child|meld": "Hepatología",
    r"diabet|insulin|hba1c|gluc": "Endocrino",
    r"abx|antib|idsa|ats": "Infecciosas",
}


def auto_tags(front: str, back: str) -> List[str]:
    text = f"{front} {back}".lower()
    tags = set()
    for rx, tag in DEFAULT_TAGS.items():
        if re.search(rx, text):
            tags.add(tag)
    toks = tokenize(text)
    # 2 términos frecuentes añadidos como "tags" auxiliares
    freq = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    top = [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:2]]
    for w in top:
        tags.add(w.capitalize())
    return sorted(tags)


# ----------------------- Persistencia -----------------------

def load_cards() -> List[Dict[str, Any]]:
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_cards(cards: List[Dict[str, Any]]):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)


def uid() -> str:
    return f"{np.random.randint(1e9)}-{int(datetime.utcnow().timestamp())}"


# ----------------------- Interfaz -----------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# Estado global
if "cards" not in st.session_state:
    st.session_state.cards = load_cards()

if "query" not in st.session_state:
    st.session_state.query = ""

if "only_due" not in st.session_state:
    st.session_state.only_due = True

if "topic_filter" not in st.session_state:
    st.session_state.topic_filter = "(Todos)"

# ------- Sidebar: importar/exportar/guardar -------
st.sidebar.header("Datos")
btn_save = st.sidebar.button("Guardar en disco (cards.json)")
if btn_save:
    save_cards(st.session_state.cards)
    st.sidebar.success("Guardado ✅")

uploaded = st.sidebar.file_uploader("Importar TSV (Frente\tReverso\tNotas)", type=["tsv", "txt"])
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded, sep="\t", header=None, names=["front", "back", "notes"], dtype=str)
        df = df.fillna("")
        new_cards = []
        for _, r in df.iterrows():
            tags = auto_tags(r["front"], r["back"]) if r["front"] or r["back"] else []
            new_cards.append(
                {
                    "id": uid(),
                    "front": r["front"],
                    "back": r["back"],
                    "notes": r["notes"],
                    "tags": tags,
                    "ef": 2.5,
                    "reps": 0,
                    "interval_days": 0,
                    "due": datetime.utcnow().isoformat(),
                }
            )
        st.session_state.cards = new_cards + st.session_state.cards
        st.sidebar.success(f"Importadas {len(new_cards)} tarjetas ✅")
    except Exception as e:
        st.sidebar.error(f"Error al importar: {e}")

if st.sidebar.button("Exportar TSV"):
    if len(st.session_state.cards) == 0:
        st.sidebar.warning("No hay tarjetas para exportar.")
    else:
        out = "\n".join(
            [
                "\t".join(
                    [
                        (c.get("front") or "").replace("\t", " "),
                        (c.get("back") or "").replace("\t", " "),
                        (c.get("notes") or "").replace("\t", " "),
                    ]
                )
                for c in st.session_state.cards
            ]
        )
        st.sidebar.download_button("Descargar flashcards.tsv", data=out, file_name="flashcards.tsv")

st.sidebar.markdown("---")
st.sidebar.caption("Consejo: guarda con frecuencia para no perder cambios.")

# ------- Filtros superiores -------
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.session_state.query = st.text_input("Búsqueda (semántica simple)", value=st.session_state.query)
with col2:
    st.session_state.only_due = st.toggle("Solo vencidas", value=st.session_state.only_due)
with col3:
    # construir lista de tags
    all_tags = sorted({t for c in st.session_state.cards for t in (c.get("tags") or [])})
    tag_choice = st.selectbox("Filtrar por etiqueta", options=["(Todos)"] + all_tags, index=0)
    st.session_state.topic_filter = tag_choice

# ------- Tabs -------
tab_manage, tab_study, tab_help = st.tabs(["Gestionar", "Estudiar", "Ayuda"])

# ===================== GESTIONAR =====================
with tab_manage:
    st.subheader("Nueva tarjeta")
    nf, nb = st.columns(2)
    with nf:
        front = st.text_area("Frente (pregunta/concepto)", height=100, key="new_front")
    with nb:
        back = st.text_area("Reverso (respuesta)", height=100, key="new_back")
    notes = st.text_area("Notas/perlas (opcional)", height=80, key="new_notes")
    if st.button("Agregar tarjeta"):
        if not front or not back:
            st.warning("Frente y Reverso son obligatorios.")
        else:
            st.session_state.cards.insert(
                0,
                {
                    "id": uid(),
                    "front": front,
                    "back": back,
                    "notes": notes,
                    "tags": auto_tags(front, back),
                    "ef": 2.5,
                    "reps": 0,
                    "interval_days": 0,
                    "due": datetime.utcnow().isoformat(),
                },
            )
            st.success("Tarjeta agregada ✅")
            st.session_state.new_front = ""
            st.session_state.new_back = ""
            st.session_state.new_notes = ""

    st.markdown("---")

    # Construir vocabulario y filtrar
    docs = [f"{c.get('front','')} {c.get('back','')} {c.get('notes','')}" for c in st.session_state.cards]
    vocab = build_vocab(docs)

    def _passes_filters(card: Dict[str, Any]) -> bool:
        # Solo vencidas si corresponde
        if st.session_state.only_due:
            due = card.get("due")
            if due and due > datetime.utcnow().isoformat():
                return False
        # Tag
        if st.session_state.topic_filter != "(Todos)":
            if st.session_state.topic_filter not in (card.get("tags") or []):
                return False
        return True

    filtered = [c for c in st.session_state.cards if _passes_filters(c)]

    # Búsqueda simple
    if st.session_state.query.strip():
        qvec = vectorize(st.session_state.query, vocab)
        scored = []
        for c in filtered:
            cvec = vectorize(
                f"{c.get('front','')} {c.get('back','')} {c.get('notes','')}",
                vocab,
            )
            scored.append((c, cosine(cvec, qvec)))
        filtered = [c for c, s in sorted(scored, key=lambda x: -x[1]) if s > 0]

    st.caption(f"Mostrando {len(filtered)} tarjetas")

    for c in filtered:
        with st.expander(c.get("front", "(sin título)")):
            colA, colB = st.columns(2)
            with colA:
                new_front = st.text_area("Frente", value=c.get("front", ""), key=f"front_{c['id']}")
                new_notes = st.text_area("Notas", value=c.get("notes", ""), key=f"notes_{c['id']}")
            with colB:
                new_back = st.text_area("Reverso", value=c.get("back", ""), key=f"back_{c['id']}")
                tags = c.get("tags") or []
                st.write("Etiquetas:", ", ".join(tags) if tags else "—")
                if st.button("Re-generar etiquetas (local)", key=f"retag_{c['id']}"):
                    c["tags"] = auto_tags(new_front, new_back)
                    st.success("Etiquetas actualizadas")
            meta1, meta2, meta3 = st.columns(3)
            with meta1:
                st.write(f"Reps: {c.get('reps', 0)} | EF: {float(c.get('ef',2.5)):.2f}")
            with meta2:
                st.write(f"Intervalo: {c.get('interval_days', 0)} días")
            with meta3:
                due = c.get("due")
                dstr = pd.to_datetime(due).strftime("%Y-%m-%d") if due else "—"
                st.write(f"Vence: {dstr}")

            ucol1, ucol2, ucol3 = st.columns(3)
            if ucol1.button("Guardar cambios", key=f"save_{c['id']}"):
                c.update({"front": new_front, "back": new_back, "notes": new_notes})
                st.success("Tarjeta actualizada")
            if ucol2.button("Limpiar etiquetas", key=f"cleartag_{c['id']}"):
                c["tags"] = []
                st.success("Etiquetas limpiadas")
            if ucol3.button("Eliminar", key=f"del_{c['id']}"):
                st.session_state.cards = [x for x in st.session_state.cards if x["id"] != c["id"]]
                st.warning("Tarjeta eliminada")

# ===================== ESTUDIAR =====================
with tab_study:
    st.subheader("Sesión de estudio")

    # Preparar cola de estudio según filtros actuales
    docs = [f"{c.get('front','')} {c.get('back','')} {c.get('notes','')}" for c in st.session_state.cards]
    vocab = build_vocab(docs)

    def _is_due(c):
        if not st.session_state.only_due:
            return True
        due = c.get("due")
        return (not due) or (due <= datetime.utcnow().isoformat())

    study_list = [c for c in st.session_state.cards if _is_due(c)]

    # Filtro por tag
    if st.session_state.topic_filter != "(Todos)":
        study_list = [c for c in study_list if st.session_state.topic_filter in (c.get("tags") or [])]

    # Búsqueda
    if st.session_state.query.strip():
        qvec = vectorize(st.session_state.query, vocab)
        scored = []
        for c in study_list:
            cvec = vectorize(
                f"{c.get('front','')} {c.get('back','')} {c.get('notes','')}",
                vocab,
            )
            scored.append((c, cosine(cvec, qvec)))
        study_list = [c for c, s in sorted(scored, key=lambda x: -x[1]) if s > 0]

    if len(study_list) == 0:
        st.info("No hay tarjetas que cumplan el filtro.")
    else:
        if "study_idx" not in st.session_state:
            st.session_state.study_idx = 0
        c = study_list[min(st.session_state.study_idx, len(study_list) - 1)]
        st.write(f"**{c.get('front','')}**")
        if st.toggle("Mostrar reverso"):
            st.write(c.get("back", ""))
            if c.get("notes"):
                st.caption(c["notes"])
            tags = c.get("tags") or []
            if tags:
                st.caption("Etiquetas: " + ", ".join(tags))

        cols = st.columns(6)
        for i, col in enumerate(cols):
            if col.button(str(i)):
                updated = schedule(c, i)
                # Reemplazar en el estado
                st.session_state.cards = [updated if x["id"] == c["id"] else x for x in st.session_state.cards]
                st.session_state.study_idx = min(st.session_state.study_idx + 1, max(0, len(study_list) - 1))
                st.rerun()

        st.caption("Califica de 0 (fallo total) a 5 (recuerdo perfecto). El planificador ajusta el próximo repaso.")

# ===================== AYUDA =====================
with tab_help:
    st.markdown(
        """
        ### ¿Cómo usar esta app?
        **1) Agregar contenido**: En la pestaña *Gestionar*, crea tarjetas manualmente o importa un archivo TSV con 3 columnas: `Frente`, `Reverso`, `Notas`.

        **2) Organizar**: Usa el filtro por etiqueta y la búsqueda. Las etiquetas se sugieren automáticamente por temática.

        **3) Estudiar**: Ve a *Estudiar*, revela la respuesta y califica de **0 a 5**. Se aplicará **SM-2** (repetición espaciada) para programar la siguiente revisión.

        **4) Guardar/respaldar**: Usa *Guardar en disco* para persistir en `cards.json`. Exporta TSV desde la barra lateral.

        ---
        **Notas técnicas**:
        - Este ejemplo no requiere API de IA. Puedes ampliarlo con un endpoint LLM si lo deseas.
        - La búsqueda usa tokens y coseno sobre bolsa de palabras (simple).
        - SM-2: primeras revisiones a 1 y 6 días; luego se incrementa según el *EF* (factor de facilidad).
        - Todo se guarda localmente; para multiusuario, considera una base de datos (SQLite + `st.connection`).
        """
    )

# Fin del archivo
