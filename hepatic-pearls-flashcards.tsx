import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';

const flashcardsData = [
  {
    front: "Patrón hepatocelular: ¿Cómo se diagnostica?",
    back: "ALT/AST ≫ FA → calcular R. Si R≥5 = hepatocelular. DDx: hepatitis viral, DILI, isquemia, NAFLD/MASLD. Perla: ALT más específica que AST."
  },
  {
    front: "¿Qué indica AST/ALT >2?",
    back: "Sugiere hepatopatía alcohólica (especialmente con GGT↑ y MCV↑). También en cirrosis avanzada. Perla: ALT puede ser normal en consumo de alcohol."
  },
  {
    front: "¿Cómo calcular el R-value y qué significa?",
    back: "R = (ALT/ULN) / (FA/ULN). R≥5: hepatocelular; R 2-5: mixto; R≤2: colestásico. Perla: usar ULN correctos del laboratorio."
  },
  {
    front: "Ley de Hy: ¿Qué indica y por qué es importante?",
    back: "ALT/AST ≥3×ULN + bilirrubina ≥2×ULN (sin FA elevada) = alto riesgo de mortalidad/insuficiencia hepática. Perla: documentar exclusión de hemólisis/obstrucción."
  },
  {
    front: "FA elevada: ¿Cómo confirmar origen hepático?",
    back: "Pedir GGT o 5'-NT. Si ambos normales → pensar en origen óseo. Si GGT↑ → origen hepático/colestasis. US es imagen de 1ª línea."
  },
  {
    front: "GGT: ¿Cuándo es útil y cuándo no?",
    back: "Útil para confirmar origen hepático de FA↑. GGT aislada es inespecífica. Perla: NO usar GGT sola para diagnosticar 'consumo de alcohol'."
  },
  {
    front: "Colestasis intra vs extrahepática: algoritmo diagnóstico",
    back: "FA/GGT↑ → US 1ª línea. Dilatación biliar = extrahepática (cálculos/tumor). Sin dilatación = intrahepática (PBC/PSC/DILI). Perla: no demorar imagen ante ictericia."
  },
  {
    front: "FIB-4: ¿Cómo se calcula y qué valores importan?",
    back: "FIB-4 = (edad×AST)/(plaquetas×√ALT). <1.3 = baja probabilidad de fibrosis (<65 años). >2.67 = sugiere fibrosis avanzada. Perla: valores intermedios requieren pruebas adicionales."
  },
  {
    front: "Transaminasas >1000: DDx principal",
    back: "Pensar en: 1) Isquemia hepática ('shock liver'), 2) Paracetamol, 3) Hepatitis A/B aguda, 4) DILI grave. Perla: LDH muy alta sugiere isquemia."
  },
  {
    front: "Isquemia hepática ('shock liver'): características",
    back: "AST/ALT >1000 + LDH muy alta en contexto de hipotensión/hipoxemia. Transaminasas caen rápido si se corrige perfusión. Perla: LDH ayuda a distinguir de viral."
  },
  {
    front: "Albúmina: ¿Qué refleja y cuándo cambiar?",
    back: "Refleja función de síntesis hepática crónica (vida media 20 días). Baja en cirrosis, nefrosis, desnutrición. Perla: no 'corregir' de rutina salvo indicación (ej. paracentesis)."
  },
  {
    front: "MELD-Na: ¿Qué es y para qué sirve?",
    back: "Usa bilirrubina, INR, creatinina y sodio. Predice mortalidad a 90 días y prioriza trasplante. Mayor MELD-Na = mayor mortalidad. Perla: usar calculadoras oficiales OPTN."
  },
  {
    front: "Child-Pugh: ¿Qué evalúa?",
    back: "Estadifica cirrosis con: bilirrubina, albúmina, INR, ascitis, encefalopatía (clases A-C). Clase C = alto riesgo. Perla: MELD-Na preferible para trasplante."
  },
  {
    front: "DILI: ¿Cuándo hospitalizar?",
    back: "Si hay: ictericia, INR↑, encefalopatía, o cumple Ley de Hy (bili≥2×ULN con ALT↑). Alto riesgo de insuficiencia hepática aguda."
  },
  {
    front: "Bilirrubina directa vs indirecta: interpretación",
    back: "Directa↑ (>50%) = colestasis/hepatitis. Indirecta↑ (>80%) = hemólisis/Gilbert. Perla: coluria señala conjugada; acolia sugiere obstrucción."
  },
  {
    front: "Síndrome de Gilbert: características",
    back: "Bilirrubina indirecta↑, FA/ALT/AST normales. Gatillado por ayuno/estrés. Benigno, no requiere imagen. Perla: educar al paciente, es benigno."
  },
  {
    front: "PBC: ¿Cómo diagnosticar?",
    back: "FA↑ + AMA-M2 (o ANA gp210/sp100). No siempre requiere biopsia. Tratamiento: UDCA 13-15 mg/kg/día. Perla: vigilar osteoporosis y tiroides."
  },
  {
    front: "PSC: ¿Cómo diagnosticar y qué vigilar?",
    back: "FA↑ + MRCP con estenosis/ectasias. Asociado a EII. Sin fármaco probado efectivo. Perla: vigilancia de colangiocarcinoma; evitar UDCA altas dosis."
  },
  {
    front: "Hepatitis B: interpretación básica de serologías",
    back: "HBsAg+/anti-HBc IgM+ = agudo. HBsAg+ >6 meses = crónico. Anti-HBs+ solo = vacunado. Perla: usar tablas CDC actualizadas."
  },
  {
    front: "Hepatitis C: ¿Por qué pedir 'reflex RNA'?",
    back: "Algoritmo 2 pasos: anticuerpo + RNA automático. Confirma infección activa en una sola orden, evita pérdidas de seguimiento. >95% curable con DAA."
  },
  {
    front: "AFP: ¿Cómo usar en vigilancia de HCC?",
    back: "US cada 6 meses ± AFP en cirróticos. AFP aislada NO suficiente para diagnóstico. Perla: elevación puede ser por hepatitis activa, no solo HCC."
  },
  {
    front: "Amonio en encefalopatía hepática: utilidad",
    back: "Uso limitado. Si amonio NORMAL, reevaluar diagnóstico de EH (considerar delirium/sepsis/fármacos). EH es diagnóstico CLÍNICO. Perla: no monitorizar seriado."
  },
  {
    front: "TP/INR en hepatopatía: interpretación",
    back: "INR↑ sugiere falla sintética. En colestasis puede ser por déficit de vitamina K. Perla: NO 'corregir' INR de rutina en cirrosis estable sin sangrado."
  },
  {
    front: "ALT 'ULN saludable': ¿Qué valores usar?",
    back: "~33 U/L varones, ~25 U/L mujeres. Valores mayores ameritan evaluación. Perla: no usar 40 U/L universal sin contexto; elevaciones leves pueden ser significativas."
  },
  {
    front: "'Red flags' de laboratorio: ¿Cuándo derivar urgente?",
    back: "INR≥1.5, bilirrubina rápida↑, ALT>1000, plaquetas<100k, Na<130. Sugiere ALF/ACLF. Calcular MELD-Na y considerar derivación a centro de trasplante."
  }
];

const FlashcardApp = () => {
  const [flashcards] = useState(flashcardsData);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [animating, setAnimating] = useState(false);

  const handleFlip = () => {
    setFlipped(!flipped);
  };

  const handleNext = () => {
    if (currentIndex < flashcards.length - 1 && !animating) {
      setAnimating(true);
      setTimeout(() => {
        setFlipped(false);
        setCurrentIndex(currentIndex + 1);
        setTimeout(() => setAnimating(false), 50);
      }, 150);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0 && !animating) {
      setAnimating(true);
      setTimeout(() => {
        setFlipped(false);
        setCurrentIndex(currentIndex - 1);
        setTimeout(() => setAnimating(false), 50);
      }, 150);
    }
  };

  const handleReset = () => {
    setCurrentIndex(0);
    setFlipped(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'ArrowLeft') handlePrevious();
    if (e.key === 'ArrowRight') handleNext();
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      e.preventDefault();
      handleFlip();
    }
  };

  React.useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentIndex, flashcards.length, flipped, animating]);

  const currentCard = flashcards[currentIndex];
  const progress = ((currentIndex + 1) / flashcards.length) * 100;

  return (
    <div className="min-h-screen" style={{ 
      background: 'linear-gradient(135deg, #134E5E 0%, #71B280 100%)'
    }}>
      {/* Header */}
      <div className="pt-8 pb-4 px-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-white text-3xl font-bold text-center mb-2">
            ⚕️ Perlas Clínicas: Pruebas Hepáticas
          </h1>
          <p className="text-white/80 text-center text-sm mb-2">
            Guía práctica para guardia y sala
          </p>
          <p className="text-white/70 text-center text-xs mb-6">
            Basado en guías AASLD, ACG, EASL, CDC
          </p>
          
          {/* Progress bar */}
          <div className="bg-white/20 rounded-full h-2.5 overflow-hidden backdrop-blur-sm">
            <div 
              className="bg-white h-full transition-all duration-300 rounded-full shadow-lg"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Flashcard */}
      <div className="flex items-center justify-center px-8 py-6">
        <div className="w-full max-w-3xl">
          <div className="relative" style={{ perspective: '1000px' }}>
            <div
              className={`relative w-full h-96 transition-all duration-700 transform-style-preserve-3d cursor-pointer ${
                flipped ? 'rotate-x-180' : ''
              } ${animating ? 'scale-95 opacity-0' : 'scale-100 opacity-100'}`}
              onClick={handleFlip}
              style={{ transformStyle: 'preserve-3d' }}
            >
              {/* Front of card */}
              <div 
                className="absolute inset-0 bg-white rounded-2xl shadow-2xl flex flex-col items-center justify-center p-10 backface-hidden"
                style={{ backfaceVisibility: 'hidden' }}
              >
                <div className="absolute top-5 left-5 bg-teal-100 text-teal-700 px-4 py-1.5 rounded-full text-sm font-bold">
                  🩺 PREGUNTA CLÍNICA
                </div>
                <div className="text-center flex-1 flex items-center justify-center px-6">
                  <h2 className="text-3xl font-bold text-gray-800 leading-tight">{currentCard.front}</h2>
                </div>
                <p className="text-gray-500 text-sm mt-auto font-medium">
                  ↑↓ o clic para ver respuesta
                </p>
              </div>
              
              {/* Back of card */}
              <div 
                className="absolute inset-0 bg-gradient-to-br from-teal-50 to-white rounded-2xl shadow-2xl flex items-center justify-center p-10 rotate-x-180 backface-hidden"
                style={{ 
                  backfaceVisibility: 'hidden',
                  transform: 'rotateX(180deg)'
                }}
              >
                <div className="absolute top-5 left-5 bg-green-100 text-green-700 px-4 py-1.5 rounded-full text-sm font-bold">
                  💡 RESPUESTA
                </div>
                <div className="text-center px-6">
                  <p className="text-xl text-gray-800 leading-relaxed whitespace-pre-line">{currentCard.back}</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex items-center justify-center mt-8 gap-4">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className={`p-4 rounded-full transition-all shadow-lg ${
                currentIndex === 0 
                  ? 'bg-white/10 text-white/30 cursor-not-allowed' 
                  : 'bg-white/25 text-white hover:bg-white/35 hover:scale-110 backdrop-blur-sm'
              }`}
              title="Anterior (←)"
            >
              <ChevronLeft size={28} />
            </button>
            
            <div className="bg-white/25 backdrop-blur-sm px-8 py-4 rounded-2xl shadow-lg">
              <span className="text-white text-xl font-bold">
                {currentIndex + 1} / {flashcards.length}
              </span>
            </div>

            <button
              onClick={handleReset}
              className="p-4 rounded-full bg-white/25 text-white hover:bg-white/35 hover:scale-110 transition-all backdrop-blur-sm shadow-lg"
              title="Reiniciar"
            >
              <RotateCcw size={28} />
            </button>
            
            <button
              onClick={handleNext}
              disabled={currentIndex === flashcards.length - 1}
              className={`p-4 rounded-full transition-all shadow-lg ${
                currentIndex === flashcards.length - 1 
                  ? 'bg-white/10 text-white/30 cursor-not-allowed' 
                  : 'bg-white/25 text-white hover:bg-white/35 hover:scale-110 backdrop-blur-sm'
              }`}
              title="Siguiente (→)"
            >
              <ChevronRight size={28} />
            </button>
          </div>

          {/* Keyboard hints */}
          <div className="mt-6 text-center space-y-2">
            <p className="text-white/70 text-sm font-medium">
              🎯 Usa ← → para navegar • ↑↓ para voltear • o clic en la tarjeta
            </p>
            <p className="text-white/60 text-xs">
              💊 Contenido basado en guías ACG 2017, AASLD, EASL, CDC 2023-2025
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Add CSS for 3D flip animation
const style = document.createElement('style');
style.textContent = `
  .rotate-x-180 {
    transform: rotateX(180deg);
  }
  .backface-hidden {
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
  }
  .transform-style-preserve-3d {
    transform-style: preserve-3d;
  }
`;
document.head.appendChild(style);

export default FlashcardApp;