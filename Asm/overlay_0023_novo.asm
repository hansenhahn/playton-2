
.nds

.open "Originais\overlay_0023.bin", "overlay_0023.bin", 0x020EFDA0

.arm                                                    ; ARM code

.org 0x020F0460
mov     r0,0x21     ;; Carrega o contador de enigmas com 33 

;; Código original
; 020F0594 E59F50E4 ldr     r5,=20889F4h
; 020F0598 E584000C str     r0,[r4,0Ch]
; 020F059C E5950000 ldr     r0,[r5]
; 020F05A0 E3A06000 mov     r6,0h
; 020F05A4 E59073EC ldr     r7,[r0,3ECh]          ;; Carrega o contador de enigmas
; 020F05A8 E1A08006 mov     r8,r6
; 020F05AC E3570000 cmp     r7,0h
; 020F05B0 DA00000D ble     20F05ECh
; 020F05B4 E5959000 ldr     r9,[r5]               ;; Carrega a memória do save
; 020F05B8 E0890108 add     r0,r9,r8,lsl 2h       ;; r8 tem a posição relativa do enigma no save
; 020F05BC E5D013F4 ldrb    r1,[r0,3F4h]          ;; Carrega o numero do enigma atual
; 020F05C0 E1A00009 mov     r0,r9
; 020F05C4 EBFE4D8D bl      2083C00h
; 020F05C8 E1A01000 mov     r1,r0
; 020F05CC E1A00009 mov     r0,r9
; 020F05D0 EBFE4DD4 bl      2083D28h
; 020F05D4 E3500000 cmp     r0,0h
; 020F05D8 03A06001 moveq   r6,1h
; 020F05DC 0A000002 beq     20F05ECh
; 020F05E0 E2888001 add     r8,r8,1h
; 020F05E4 E1580007 cmp     r8,r7
; 020F05E8 BAFFFFF1 blt     20F05B4h

.org 0x020F05A4
mov     r7,0x21    ;; Carrega o contador de enigmas com 33 

.org 0x020F05BC
bl   0x02045960     ;; Jump para o arm9.bin

.close