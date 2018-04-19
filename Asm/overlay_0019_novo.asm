
.nds

.open "Originais\overlay_0019.bin", "overlay_0019.bin", 0x020EFDA0

.arm                                                    ; ARM code

; 020F2398 E92D4008 push    r3,r14
; 020F239C E3A02000 mov     r2,0h
; 020F23A0 E580254C str     r2,[r0,54Ch]
; 020F23A4 E59F30D4 ldr     r3,=20889F4h
; 020F23A8 E5802560 str     r2,[r0,560h]
; 020F23AC E5931000 ldr     r1,[r3]
; 020F23B0 E591C3EC ldr     r12,[r1,3ECh]         ;; Carrega o contador de enigma
; 020F23B4 E580C548 str     r12,[r0,548h]
; 020F23B8 E35C0000 cmp     r12,0h
; 020F23BC DA000019 ble     20F2428h
; 020F23C0 E1A01000 mov     r1,r0
; 020F23C4 E593E000 ldr     r14,[r3]
; 020F23C8 E080C102 add     r12,r0,r2,lsl 2h
; 020F23CC E08EE102 add     r14,r14,r2,lsl 2h
; 020F23D0 E5DEE3F4 ldrb    r14,[r14,3F4h]        ;; Carrega o número do enigma atual
; 020F23D4 E58CE080 str     r14,[r12,80h]
; 020F23D8 E590C550 ldr     r12,[r0,550h]
; 020F23DC E15C000E cmp     r12,r14
; 020F23E0 0580254C streq   r2,[r0,54Ch]
; 020F23E4 E593C000 ldr     r12,[r3]
; 020F23E8 E08CC102 add     r12,r12,r2,lsl 2h
; 020F23EC E5DCC3F5 ldrb    r12,[r12,3F5h]
; 020F23F0 E581C5E8 str     r12,[r1,5E8h]
; 020F23F4 E593C000 ldr     r12,[r3]
; 020F23F8 E08CC102 add     r12,r12,r2,lsl 2h
; 020F23FC E5DCC3F6 ldrb    r12,[r12,3F6h]
; 020F2400 E581C5EC str     r12,[r1,5ECh]
; 020F2404 E593C000 ldr     r12,[r3]
; 020F2408 E08CC102 add     r12,r12,r2,lsl 2h
; 020F240C E5DCC3F7 ldrb    r12,[r12,3F7h]
; 020F2410 E2822001 add     r2,r2,1h
; 020F2414 E581C5F0 str     r12,[r1,5F0h]
; 020F2418 E590C548 ldr     r12,[r0,548h]
; 020F241C E281100C add     r1,r1,0Ch
; 020F2420 E152000C cmp     r2,r12
; 020F2424 BAFFFFE6 blt     20F23C4h
; 020F2428 E35C0005 cmp     r12,5h
; 020F242C D3A01000 movle   r1,0h
; 020F2430 D580154C strle   r1,[r0,54Ch]
; 020F2434 DA000003 ble     20F2448h
; 020F2438 E590154C ldr     r1,[r0,54Ch]
; 020F243C E24C2005 sub     r2,r12,5h
; 020F2440 E1510002 cmp     r1,r2
; 020F2444 C580254C strgt   r2,[r0,54Ch]
; 020F2448 E5903548 ldr     r3,[r0,548h]
; 020F244C E3530099 cmp     r3,99h
; 020F2450 AA000005 bge     20F246Ch
; 020F2454 E3A02000 mov     r2,0h
; 020F2458 E0801103 add     r1,r0,r3,lsl 2h
; 020F245C E2833001 add     r3,r3,1h
; 020F2460 E5812080 str     r2,[r1,80h]
; 020F2464 E3530099 cmp     r3,99h
; 020F2468 BAFFFFFA blt     20F2458h
; 020F246C E5901550 ldr     r1,[r0,550h]
; 020F2470 E3510000 cmp     r1,0h
; 020F2474 05901080 ldreq   r1,[r0,80h]
; 020F2478 05801550 streq   r1,[r0,550h]
; 020F247C E8BD8008 pop     r3,r15

.org 0x020F23B0
mov     r12,0x21

.org 0x020F23D0
bl      0x02045908

.close