from pathlib import Path
import runpy
runpy.run_path('.github/scripts/patch_bordatto_041_ui1.py', run_name='__main__')
path=Path('BORDATTO_Foundation_0.1/app/src/main/java/com/bordatto/app/MainActivity.kt')
text=path.read_text(encoding='utf-8')
safe=text.index('@Composable\nprivate fun SafeEditorPanel(')
ui=r'''@Composable
private fun ThreadPalettePanel(design:Design,onChangeColor:(Int,Int)->Unit){
    var expanded by remember(design.name){mutableStateOf(false)}
    var editIndex by remember{mutableStateOf<Int?>(null)}
    var hex by remember{mutableStateOf("")}
    val stats=remember(design){calculateThreadColorStats(design)}
    val blocks=remember(design){calculateThreadBlocks(design)}
    val meters=stats.sumOf{it.estimatedMeters.toDouble()}
    Surface(shape=RoundedCornerShape(16.dp),color=CardBrown,border=androidx.compose.foundation.BorderStroke(1.dp,Gold.copy(alpha=.36f))){
        Column(Modifier.fillMaxWidth().padding(11.dp),verticalArrangement=Arrangement.spacedBy(8.dp)){
            Row(Modifier.fillMaxWidth().clickable{expanded=!expanded},verticalAlignment=Alignment.CenterVertically){
                Icon(Icons.Rounded.Palette,null,tint=Gold,modifier=Modifier.size(19.dp)); Spacer(Modifier.width(7.dp))
                Column(Modifier.weight(1f)){
                    Text("Cores & Linhas",color=Cream,fontSize=10.sp,fontWeight=FontWeight.SemiBold)
                    Text("${stats.size} cores • ${blocks.size} blocos • ~${"%.1f".format(meters)} m (+12%)",color=Muted,fontSize=7.sp)
                }
                Icon(if(expanded) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore,null,tint=Gold)
            }
            if(expanded){
                Text("Sequência: "+blocks.take(12).joinToString(" › "){"${it.sequence}:C${it.colorIndex+1}"}+if(blocks.size>12)" › +${blocks.size-12}" else "",color=Muted,fontSize=7.sp)
                stats.take(32).forEach{stat->
                    val info=stat.info; val jef=remember(stat.color){nearestJefThread(stat.color)}
                    Surface(shape=RoundedCornerShape(12.dp),color=SurfaceBrown,border=androidx.compose.foundation.BorderStroke(1.dp,LineGold.copy(alpha=.28f))){
                        Column(Modifier.fillMaxWidth().padding(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){
                            Row(verticalAlignment=Alignment.CenterVertically){
                                Box(Modifier.size(24.dp).clip(CircleShape).background(Color(stat.color)).border(1.dp,Cream.copy(alpha=.3f),CircleShape)); Spacer(Modifier.width(7.dp))
                                Column(Modifier.weight(1f)){
                                    Text(info?.name?.takeIf{it.isNotBlank()}?:"Cor ${stat.index+1}",color=Cream,fontSize=9.sp,fontWeight=FontWeight.SemiBold,maxLines=1)
                                    Text(buildString{append(formatThreadHex(stat.color));info?.catalog?.takeIf{it.isNotBlank()}?.let{append(" • Cat. $it")};info?.brand?.takeIf{it.isNotBlank()}?.let{append(" • $it")}},color=Muted,fontSize=7.sp,maxLines=1)
                                }
                                IconButton(onClick={editIndex=stat.index;hex=formatThreadHex(stat.color)}){Icon(Icons.Rounded.Edit,"Editar RGB",tint=Gold,modifier=Modifier.size(17.dp))}
                            }
                            Text("${stat.stitchCount} pts • ${"%.1f".format(stat.percent)}% • ~${"%.2f".format(stat.estimatedMeters)} m • ${stat.blockCount} bloco${if(stat.blockCount==1)"" else "s"}",color=Muted,fontSize=7.sp)
                            Text(if(jef.exactRgb)"JEF: RGB exato • ${jef.name} (${jef.catalog})" else "JEF: aproxima → ${jef.name} (${jef.catalog}) ${formatThreadHex(jef.color)}",color=if(jef.exactRgb)Gold else Muted,fontSize=7.sp)
                        }
                    }
                }
                if(stats.size>32) Text("Exibindo 32 de ${stats.size} cores para manter o painel leve.",color=Muted,fontSize=7.sp)
                Text("Linha estimada pela geometria + 12% de reserva. Editar RGB altera só a cópia de trabalho e pode ser desfeito/refeito.",color=Muted,fontSize=7.sp,lineHeight=10.sp)
            }
        }
    }
    editIndex?.let{index->
        val parsed=parseThreadHex(hex)
        AlertDialog(
            onDismissRequest={editIndex=null},
            title={Text("Editar cor ${index+1}",color=Gold,fontFamily=FontFamily.Serif)},
            text={Column(verticalArrangement=Arrangement.spacedBy(9.dp)){
                OutlinedTextField(value=hex,onValueChange={hex=it.take(9)},singleLine=true,label={Text("RGB hexadecimal")},placeholder={Text("#E1B66F")},leadingIcon={Box(Modifier.size(20.dp).clip(CircleShape).background(Color(parsed?:effectiveThreadColor(design,index))))},colors=OutlinedTextFieldDefaults.colors(focusedBorderColor=Gold,unfocusedBorderColor=LineGold))
                parsed?.let{c->val m=nearestJefThread(c);Text(if(m.exactRgb)"JEF: correspondência exata • ${m.name}" else "JEF converterá para ${m.name} ${formatThreadHex(m.color)}",color=Muted,fontSize=8.sp)}
            }},
            confirmButton={TextButton(enabled=parsed!=null,onClick={parsed?.let{onChangeColor(index,it)};editIndex=null}){Text("Aplicar")}},
            dismissButton={TextButton(onClick={editIndex=null}){Text("Cancelar")}}
        )
    }
}

'''
text=text[:safe]+ui+text[safe:]
text=text.replace('0.2.19','0.2.20')
path.write_text(text,encoding='utf-8')
print('BORDATTO 0.2.20 colors UI applied')
