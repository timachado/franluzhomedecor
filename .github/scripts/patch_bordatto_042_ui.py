from pathlib import Path
import runpy

runpy.run_path('.github/scripts/patch_bordatto_042_core.py', run_name='__main__')
path=Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text=path.read_text(encoding='utf-8')

insert_at=text.index('@Composable\nprivate fun ThreadPalettePanel(')
dialog=r'''@Composable
private fun ThreadCatalogDialog(
    colorIndex:Int,
    design:Design,
    onDismiss:()->Unit,
    onApply:(DesignThreadInfo)->Unit
){
    val currentColor=effectiveThreadColor(design,colorIndex)
    var query by remember(colorIndex){mutableStateOf("")}
    var brand by remember(colorIndex){mutableStateOf("Todos")}
    val results=remember(query,brand,currentColor){catalogSearchResults(query,brand,currentColor)}
    val best=remember(brand,currentColor){catalogSearchResults("",brand,currentColor).firstOrNull()}
    AlertDialog(
        onDismissRequest=onDismiss,
        title={Column{
            Text("Catálogo de Linhas",color=Gold,fontFamily=FontFamily.Serif)
            Text("Cor ${colorIndex+1} • ${formatThreadHex(currentColor)}",color=Muted,fontSize=9.sp)
        }},
        text={Column(Modifier.fillMaxWidth().heightIn(max=520.dp),verticalArrangement=Arrangement.spacedBy(9.dp)){
            OutlinedTextField(
                value=query,onValueChange={query=it.take(40)},modifier=Modifier.fillMaxWidth(),singleLine=true,
                leadingIcon={Icon(Icons.Rounded.Search,null,tint=Gold)},label={Text("Nome, código ou HEX")},
                placeholder={Text("Ex.: 13, Gold, #E4C35D")},
                colors=OutlinedTextFieldDefaults.colors(focusedBorderColor=Gold,unfocusedBorderColor=LineGold)
            )
            Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(6.dp)){
                listOf("Todos","Brother","Janome").forEach{option->
                    FilterChip(
                        selected=brand==option,onClick={brand=option},label={Text(option,fontSize=8.sp)},
                        colors=FilterChipDefaults.filterChipColors(selectedContainerColor=Gold.copy(alpha=.18f),selectedLabelColor=Gold)
                    )
                }
            }
            if(query.isBlank()) best?.let{entry->
                val d=rgbCatalogDistance(currentColor,entry.info.color)
                Surface(
                    modifier=Modifier.fillMaxWidth().clickable{onApply(entry.info);onDismiss()},shape=RoundedCornerShape(14.dp),
                    color=Gold.copy(alpha=.10f),border=androidx.compose.foundation.BorderStroke(1.dp,Gold.copy(alpha=.38f))
                ){
                    Row(Modifier.fillMaxWidth().padding(9.dp),verticalAlignment=Alignment.CenterVertically){
                        Icon(Icons.Rounded.AutoAwesome,null,tint=Gold,modifier=Modifier.size(18.dp));Spacer(Modifier.width(7.dp))
                        Column(Modifier.weight(1f)){
                            Text("Sugestão inteligente",color=Gold,fontSize=8.sp,fontWeight=FontWeight.Bold)
                            Text("${entry.info.brand} ${entry.info.catalog} • ${entry.info.name}",color=Cream,fontSize=8.sp,maxLines=1)
                            Text("${formatThreadHex(entry.info.color)} • ${rgbCatalogQuality(d)} • ΔRGB $d",color=Muted,fontSize=7.sp)
                        }
                        Icon(Icons.Rounded.ChevronRight,null,tint=Gold)
                    }
                }
            }
            Text(if(query.isBlank())"Mais próximas da cor atual" else "${results.size} resultado${if(results.size==1)"" else "s"}",color=Muted,fontSize=8.sp)
            LazyColumn(Modifier.fillMaxWidth().heightIn(max=310.dp),verticalArrangement=Arrangement.spacedBy(6.dp)){
                results.take(40).forEach{entry->
                    item(key="${entry.info.brand}-${entry.info.catalog}-${entry.info.color}"){
                        val d=rgbCatalogDistance(currentColor,entry.info.color)
                        Surface(
                            modifier=Modifier.fillMaxWidth().clickable{onApply(entry.info);onDismiss()},shape=RoundedCornerShape(12.dp),
                            color=SurfaceBrown,border=androidx.compose.foundation.BorderStroke(1.dp,LineGold.copy(alpha=.28f))
                        ){
                            Row(Modifier.fillMaxWidth().padding(8.dp),verticalAlignment=Alignment.CenterVertically){
                                Box(Modifier.size(28.dp).clip(CircleShape).background(Color(entry.info.color)).border(1.dp,Cream.copy(alpha=.30f),CircleShape));Spacer(Modifier.width(8.dp))
                                Column(Modifier.weight(1f)){
                                    Text("${entry.info.brand} • ${entry.info.catalog}",color=Gold,fontSize=8.sp,fontWeight=FontWeight.SemiBold)
                                    Text(entry.info.name.ifBlank{"Sem nome"},color=Cream,fontSize=8.sp,maxLines=1)
                                    Text("${formatThreadHex(entry.info.color)} • ${rgbCatalogQuality(d)} • ΔRGB $d",color=Muted,fontSize=7.sp)
                                }
                                Icon(Icons.Rounded.CheckCircle,"Aplicar",tint=Gold,modifier=Modifier.size(18.dp))
                            }
                        }
                    }
                }
            }
            Text("ΔRGB é uma aproximação matemática. Brilho, material da linha, tecido e iluminação podem mudar a aparência física.",color=Muted,fontSize=7.sp,lineHeight=10.sp)
        }},
        confirmButton={},
        dismissButton={TextButton(onClick=onDismiss){Text("Fechar")}}
    )
}

'''
text=text[:insert_at]+dialog+text[insert_at:]

start=text.index('@Composable\nprivate fun ThreadPalettePanel(')
end=text.index('\n@Composable\nprivate fun SafeEditorPanel(',start)
segment=text[start:end]
segment=segment.replace(
'private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit){',
'private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit,onApplyCatalogThread:(Int,DesignThreadInfo)->Unit){',1)
segment=segment.replace(
'    var editIndex by remember{mutableStateOf<Int?>(null)}\n',
'    var editIndex by remember{mutableStateOf<Int?>(null)}\n    var catalogIndex by remember{mutableStateOf<Int?>(null)}\n',1)
segment=segment.replace(
'                                IconButton(onClick={editIndex=stat.index;hex=formatThreadHex(stat.color)}){Icon(Icons.Rounded.Edit,"Editar RGB",tint=Gold,modifier=Modifier.size(17.dp))}',
'                                IconButton(onClick={catalogIndex=stat.index}){Icon(Icons.Rounded.Search,"Catálogo de linhas",tint=Gold,modifier=Modifier.size(17.dp))}\n                                IconButton(onClick={editIndex=stat.index;hex=formatThreadHex(stat.color)}){Icon(Icons.Rounded.Edit,"Editar RGB",tint=Gold,modifier=Modifier.size(17.dp))}',1)
extra='''\n    catalogIndex?.let{index->\n        ThreadCatalogDialog(\n            colorIndex=index,design=design,onDismiss={catalogIndex=null},\n            onApply={selected->onApplyCatalogThread(index,selected)}\n        )\n    }\n'''
close=segment.rfind('\n}')
if close<0: raise SystemExit('ThreadPalettePanel closing marker not found')
segment=segment[:close]+extra+segment[close:]
text=text[:start]+segment+text[end:]
text=text.replace('0.2.20','0.2.21')
path.write_text(text,encoding='utf-8')
print('BORDATTO 0.2.21 thread catalog UI applied')
