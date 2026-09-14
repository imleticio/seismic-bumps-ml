import {FileBlob,PresentationFile} from '@oai/artifact-tool';const p=await PresentationFile.importPptx(await FileBlob.load('/Users/leonel/Desktop/TAD/tmp/presentation-simple-light/template-starter.pptx'));const ch=p.slides.items[7].charts.items[0];
for(const k of ['barOptions','legend','xAxis','yAxis','dataLabels','chartFill','plotAreaFill','chartLine','plotAreaLine']){const x=ch[k]; console.log(k,x?.constructor?.name,Object.keys(x||{}),Object.getOwnPropertyNames(Object.getPrototypeOf(x||{})));}
console.log('apply len',ch.apply.length,ch.apply.toString().slice(0,400));
