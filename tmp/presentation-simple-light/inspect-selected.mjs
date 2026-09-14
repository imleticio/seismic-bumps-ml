import fs from 'node:fs/promises';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/leonel/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.0/skills/artifact-template-simple-light-mode/assets/reference.pptx'));
const x=await p.inspect({kind:'slide,textbox,shape,image,table,chart,notes,layout',max_chars:500000});
await fs.writeFile('/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-full.ndjson',x.ndjson||'');
console.log((x.ndjson||'').length);
