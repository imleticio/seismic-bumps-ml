import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-starter.pptx'));
for(const id of ['sh/idcnmx8j','im/rydcn2p8','ch/ip4jm5kr','sh/wvexc3qx']){const x=p.resolve(id); console.log(id, x?.constructor?.name, Object.keys(x||{}), Object.getOwnPropertyNames(Object.getPrototypeOf(x||{})));}
console.log('help delete', (await p.help('*',{search:'delete shape remove element collection',include:['index','examples','notes'],maxChars:5000})).text||'');
const ch=p.resolve('ch/ip4jm5kr'); console.log('chart series count',ch.series?.count); for(let i=0;i<(ch.series?.count||0);i++){let s=ch.series.getItemAt(i); console.log(i,s?.constructor?.name,Object.keys(s||{}),Object.getOwnPropertyNames(Object.getPrototypeOf(s||{})),s.name,s.values,s.categories,s.fill,s.line);}
