import fs from 'node:fs/promises';
const base='/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-inspect/layouts';
const mappings=[
[1,'Portada del proyecto'],[4,'Problema, riesgo y pregunta de investigación'],[4,'Objetivo general'],[16,'Ocho objetivos específicos'],[8,'Conjunto de datos y desbalance'],[8,'Protocolo común de evaluación'],[8,'Preparación de datos y SMOTE'],[22,'Resultados de modelos base'],[20,'Resultados de variantes con SMOTE'],[8,'Evidencia ROC antes de la selección'],[12,'Modelo seleccionado y matriz de confusión'],[8,'Sensibilidad complementaria a la cantidad de atributos'],[15,'Conclusiones, limitaciones y próximos pasos']
];
const actionFor=(el)=>{
 const nm=(el.name||'').toLowerCase();
 if(nm.includes('footer')) return 'delete';
 if(nm.includes('slide number')) return 'rewrite';
 if(el.kind==='image') return 'replace';
 if(el.kind==='chart'||el.kind==='table'||(el.text!=null)) return 'rewrite';
 return 'keep';
};
const outputSlides=[];
for(let i=0;i<mappings.length;i++){
 const [src,role]=mappings[i];
 const layout=JSON.parse(await fs.readFile(`${base}/source-slide-${String(src).padStart(2,'0')}.layout.json`,'utf8'));
 const editTargets=layout.elements.map(el=>({shapeId:el.aid,action:actionFor(el),reason:`Adapt inherited ${el.kind} for ${role}`})).filter(x=>x.action!=='keep');
 outputSlides.push({outputSlide:i+1,sourceSlide:src,narrativeRole:role,reuseMode:'duplicate-slide',editTargets});
}
const used=new Set(mappings.map(x=>x[0]));
const omittedSourceSlides=[]; for(let i=1;i<=26;i++) if(!used.has(i)) omittedSourceSlides.push({sourceSlide:i,reason:'Layout pattern not required by the 13-slide narrative.'});
await fs.writeFile('/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-frame-map.json',JSON.stringify({outputSlides,omittedSourceSlides},null,2));
