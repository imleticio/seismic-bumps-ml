import fs from 'node:fs/promises';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/leonel/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.0/skills/artifact-template-simple-light-mode/assets/reference.pptx'));
let all=[];
for(let i=1;i<=26;i++){
 const lp=`/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-inspect/layouts/source-slide-${String(i).padStart(2,'0')}.layout.json`;
 const l=JSON.parse(await fs.readFile(lp,'utf8')); const id=l.slide.aid;
 const x=await p.inspect({target:{id,beforeLines:0,afterLines:200},kind:'slide,textbox,shape,image,table,chart',max_chars:50000});
 const lines=(x.ndjson||'').split('\n').filter(Boolean).filter(s=>!s.includes('"kind":"notice"'));
 all.push(...lines);
}
const seen=new Set(); const uniq=[]; for(const l of all){const o=JSON.parse(l); const k=o.kind+'|'+o.id; if(!seen.has(k)){seen.add(k);uniq.push(l)}}
await fs.writeFile('/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-inspect/template-inspect.ndjson',uniq.join('\n')+'\n'); console.log({lines:uniq.length});
