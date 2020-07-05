
.nds

.open "Originais\overlay_0011.bin", "overlay_0011.bin", 0x020EFDA0

.arm                                                    ; ARM code

.org 0x020F01BC
cmp		r1,r1     ;; Compara o valor lido com ele mesmo (sendo assim sempre verdadeiro)

;; Código original
; 020F0160 E92D47F0 push    r4-r10,r14                              ;1  119
; 020F0164 E24DD008 sub     r13,r13,8h                              ;1  120
; 020F0168 E59F10F8 ldr     r1,=20889F4h                            ;2  122
; 020F016C E1A04000 mov     r4,r0                                   ;1  123
; 020F0170 E5910000 ldr     r0,[r1]                                 ;3  126
; 020F0174 E5D00478 ldrb    r0,[r0,478h]                            ;3  129
; 020F0178 E3500029 cmp     r0,29h                                  ;1  130
; 020F017C 1A000003 bne     20F0190h                                ;3  133
; 020F0180 E59F10E4 ldr     r1,=4E4Bh                               ;2  135
; 020F0184 E28D0000 add     r0,r13,0h                               ;1  136
; 020F0188 EBFDEE2E bl      206BA48h                                ;3  139
; 020F018C EA000004 b       20F01A4h                                ;3  142
; 020F0190 E350002A cmp     r0,2Ah                                  ;1  143
; 020F0194 1A000002 bne     20F01A4h                                ;3  146
; 020F0198 E59F10D0 ldr     r1,=4B55h                               ;2  148
; 020F019C E28D0000 add     r0,r13,0h                               ;1  149
; 020F01A0 EBFDEE28 bl      206BA48h                                ;3  152
; 020F01A4 E28D5000 add     r5,r13,0h                               ;1  153
; 020F01A8 E3A02001 mov     r2,1h                                   ;1  154
; 020F01AC E3A03000 mov     r3,0h                                   ;1  155
; 020F01B0 E0840003 add     r0,r4,r3                                ;1  156
; 020F01B4 E5D51000 ldrb    r1,[r5]                                 ;3  159  Lê um byte da hash inserida pelo usuário
; 020F01B8 E5D00004 ldrb    r0,[r0,4h]                              ;3  162	 Lê um byte da hash gerada pelo jogo no endereço 027E36F8
; 020F01BC E1510000 cmp     r1,r0                                   ;1  163  Compara uma com a outra
; 020F01C0 13A02000 movne   r2,0h                                   ;1  164
; 020F01C4 1A000003 bne     20F01D8h                                ;3  167
; 020F01C8 E2833001 add     r3,r3,1h                                ;1  168
; 020F01CC E3530008 cmp     r3,8h                                   ;1  169
; 020F01D0 E2855001 add     r5,r5,1h                                ;1  170
; 020F01D4 BAFFFFF5 blt     20F01B0h                                ;3  173
; 020F01D8 E3520000 cmp     r2,0h                                   ;1  174
; 020F01DC 128DD008 addne   r13,r13,8h                              ;1  175
; 020F01E0 13A00000 movne   r0,0h                                   ;1  176
; 020F01E4 18BD87F0 popne   r4-r10,r15                              ;4  180
; 020F01E8 E3A09001 mov     r9,1h                                   ;1  181
; 020F01EC E59FA080 ldr     r10,=2088A60h                           ;2  183
; 020F01F0 E59F6080 ldr     r6,=2088B98h                            ;2  185
; 020F01F4 E59F5080 ldr     r5,=2088AD4h                            ;2  187
; 020F01F8 E1A08009 mov     r8,r9                                   ;1  188
; 020F01FC E3A0701F mov     r7,1Fh                                  ;1  189
; 020F0200 E1A0000A mov     r0,r10                                  ;1  190
; 020F0204 EBFDF16A bl      206C7B4h                                ;3  193
; 020F0208 E1A00004 mov     r0,r4                                   ;1  194
; 020F020C EB0000D6 bl      20F056Ch                                ;3  197
; 020F0210 E5940038 ldr     r0,[r4,38h]                             ;3  200
; 020F0214 E1A01009 mov     r1,r9                                   ;1  201
; 020F0218 E1A02009 mov     r2,r9                                   ;1  202
; 020F021C EBFE4110 bl      2080664h                                ;3  205
; 020F0220 E594003C ldr     r0,[r4,3Ch]                             ;3  208
; 020F0224 E1A01008 mov     r1,r8                                   ;1  209
; 020F0228 E1A02008 mov     r2,r8                                   ;1  210
; 020F022C EBFE410C bl      2080664h                                ;3  213
; 020F0230 E59400D0 ldr     r0,[r4,0D0h]                            ;3  216
; 020F0234 E1A01007 mov     r1,r7                                   ;1  217
; 020F0238 EBFE1704 bl      2075E50h                                ;3  220
; 020F023C E1A00006 mov     r0,r6                                   ;1  221
; 020F0240 EBFDF35C bl      206CFB8h                                ;3  224
; 020F0244 E1A00005 mov     r0,r5                                   ;1  225
; 020F0248 EBFDF7EA bl      206E1F8h                                ;3  228
; 020F024C E3500000 cmp     r0,0h                                   ;1  229
; 020F0250 0AFFFFEA beq     20F0200h                                ;3  232
; 020F0254 E1A00004 mov     r0,r4                                   ;1  233
; 020F0258 EB000008 bl      20F0280h                                ;3  236
; 020F025C E3A00001 mov     r0,1h                                   ;1  237
; 020F0260 E28DD008 add     r13,r13,8h                              ;1  238
; 020F0264 E8BD87F0 pop     r4-r10,r15                              ;4  242
; 020F0268 020889F4 andeq   r8,r8,3D0000h                           ;1  243
; 020F026C 00004E4B andeq   r4,r0,r11,asr 1Ch                       ;1  244
; 020F0270 00004B55 andeq   r4,r0,r5,asr r11                        ;2  246
; 020F0274 02088A60 andeq   r8,r8,60000h                            ;1  247
; 020F0278 02088B98 andeq   r8,r8,26000h                            ;1  248
; 020F027C 02088AD4 andeq   r8,r8,0D4000h                           ;1  249

.close