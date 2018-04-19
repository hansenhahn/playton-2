;; especificação
;; cabeçalho:
;; word[-1] : somar ao tamanho do arquivo comprimido para ter o arquivo descomprimido
;; word[-2] : 3 bytes: tamanho do arquivo comprimido
;;          : 1 byte:  subtrair do fim do arquivo comprimido para indicar onde começam os dados
;; a compressão é feita de trás pra frente
;; flag 8 bits
;; 1 -> comprimido, 0 -> não comprimido
;; par lz: distância máxima 0xFFF + 2
;; par lz: tamanho máximo 0xF + 2
02000978 E92D00F0 push    r4-r7
0200097C E9100006 ldmdb   [r0],r1,r2
02000980 E0802002 add     r2,r0,r2
02000984 E0403C21 sub     r3,r0,r1,lsr 18h
02000988 E3C114FF bic     r1,r1,0FF000000h
0200098C E0401001 sub     r1,r0,r1
02000990 E1A04002 mov     r4,r2
02000994 E1530001 cmp     r3,r1
02000998 DA000015 ble     20009F4h
0200099C E5735001 ldrb    r5,[r3,-1h]!          ; Lê um byte pra trás a flag
020009A0 E3A06008 mov     r6,8h                 ; Flag de 8 bits
020009A4 E2566001 subs    r6,r6,1h              ; Itera 1
020009A8 BAFFFFF9 blt     2000994h              ; Se o iterador chegou a 0, salta pro começo
020009AC E3150080 tst     r5,80h                ; Testa o bit7 da flag
020009B0 1A000002 bne     20009C0h              ; Se 1, está comprimido, se 0, não está comprimido
020009B4 E5730001 ldrb    r0,[r3,-1h]!          ; Lê um byte pra trás do arquivo e retrocede
020009B8 E5620001 strb    r0,[r2,-1h]!          ; Grava um byte pra trás na saída e retrocede
020009BC EA000009 b       20009E8h              ; Salta
020009C0 E573C001 ldrb    r12,[r3,-1h]!         ; Lê um byte pra trás do arquivo (par lz)
020009C4 E5737001 ldrb    r7,[r3,-1h]!          ; Lê um byte pra trás do arquivo (par lz)
020009C8 E187740C orr     r7,r7,r12,lsl 8h      ; par lz = (r12 << 8 | r7)
020009CC E3C77A0F bic     r7,r7,0F000h          ; r7 = par lz & 0x0FFF
020009D0 E2877002 add     r7,r7,2h              ; r7 += 2   distância
020009D4 E28CC020 add     r12,r12,20h           ; r12 += 20 quantidade
020009D8 E7D20007 ldrb    r0,[r2,r7]            ; Lê do buffer
020009DC E5620001 strb    r0,[r2,-1h]!          ; Grava no buffer e retrocede
020009E0 E25CC010 subs    r12,r12,10h           ; Subtrai um da quantidade
020009E4 AAFFFFFB bge     20009D8h              ; Copia até zerar a quantidade
020009E8 E1530001 cmp     r3,r1                 ; Verifica se chegou ao fim
020009EC E1A05085 mov     r5,r5,lsl 1h          ; Desloca a flag << 1
020009F0 CAFFFFEB bgt     20009A4h              ; Se não chegou ao fim, volta pro começo da iteração
020009F4 E3A00000 mov     r0,0h                 ; Caso contrário, retorna
020009F8 E3C1301F bic     r3,r1,1Fh
020009FC EE070F9A mov     p15,0,c7,c10,4,r0 ;Drain Write Buffer
02000A00 EE073F35 mov     p15,0,c7,c5,1,r3 ;VA Invalidate Instruction Cache Line
02000A04 EE073F3E mov     p15,0,c7,c14,1,r3 ;VA Clean/Invalidate Data Cache Line
02000A08 E2833020 add     r3,r3,20h
02000A0C E1530004 cmp     r3,r4
02000A10 BAFFFFF9 blt     20009FCh
02000A14 E8BD00F0 pop     r4-r7
02000A18 E12FFF1E bx      r14
