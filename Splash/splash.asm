.nds

.open "arm9_original.bin", "arm9_splash.bin",0x2000000
.arm

.org 0x2000bb4      ; Desliga a compressão do arm9.bin
.dw 0


.org 0x2000800
b 0x20469d8

.org 0x20469d8

entry_point equ 0x02000800

image_address	equ 0x02300000
image_size		equ 0x18000
base_address    equ 0x02200000

main:
	; sets POWER_CR
	
mov r0, #0x4000000
orr r0, r0, #0x300
orr r0, r0, #0x4
ldr r1,=0x820F
strh r1, [r0]

	; sets mode
; Engine A
mov r0, #0x04000000
ldr r1,=0x10405
str r1, [r0]
mov r1, #0x8
strb r1, [r0,0x4]
; A-BG2CNT
mov r1, #0x4000
orr r1, r1, #0x80
strh r1, [r0,0xC]

mov r1, #0x100
strh r1, [r0,0x20]
strh r1, [r0,0x26]


; Engine B
mov r0, #0x04000000
orr r0, r0, #0x1000
ldr r1,=0x10405
str r1, [r0]
mov r1, #0x9
strb r1, [r0, 0x4]
; B-BG2CNT
mov r1, #0x4000
orr r1, r1, #0x80
strh r1, [r0, 0xC]

mov r1, #0x100
strh r1, [r0,0x20]
strh r1, [r0,0x26]
 
; sets VRAM bank A
mov r0, #0x04000000
add r0, r0, #0x240
mov r1, #0x81
strb r1, [r0]
mov r1, #0x82
strb r1, [r0,0x1]
; sets VRAM bank C
mov r1, #0x84
strb r1, [r0,0x2]
strb r1, [r0,0x3]

mov r1, #0x8000
orr r1, #0x10
mov r0, #0x04000000         
add r0, r0, #0x6c
str r1,[r0]                 ; Seta o master bright da engine A (para fazer o fade in)
orr r0, #0x1000             
str r1,[r0]                 ; Seta o master bright da engine B (para fazer o fade in)

; Rotina de descompressão da splash
decompress_main:
ldr r0,=base_address
ldr r5,=credits_image
ldrh r1,[r5]
strh r1, [r0, 0x2]
add r5, #0x2
lsl r1, r1, 0x1
add r1, r5, r1
str r1, [r0, 0x4] 			; Início dos dados comprimidos
ldr r1,=image_address
str r1,[r0, 0x8]
str r5,[r0, 0xc]
str r1,[r0, 0x10]
ldr r4,=image_size
str r4,[r0, 0x14]
mov r7, r0

decompress_start:
ldr r0,[r7, 0xc]
ldrh r4,[r0]
add r0,#0x2
str r0,[r7, 0xc]
mov r0, r4
mov r1, #0x8000
and r0,r1
lsl r0,r0,0x10
lsr r0,r0,0x10
cmp r0,#0x0
beq decompress_from_rom

decompress_from_ram:
lsr r0,r4,0xa
mov r1,#0x1f
and r0,r1
add r6,r0,0x2
lsl r5,r6,0x1 			; WORD COUNT * 2
ldr r0,=0x3ff
and r4,r0
lsl r3,r4,0x1
ldr r2,[r7,0x10]
sub r1,r2,r3

ldr r0,=0x040000D4
str r1,[r0]
add r0, #0x4
str r2,[r0]
add r0, #0x4
mov r1, #0x80
lsl r1, r1, 0x18
orr r1, r1, r3
str r1,[r0]
ldr r1,[r0]

add r2,r2,r5
str r2,[r7,0x10]
b decompress_end

decompress_from_rom:
mov r6,r4
lsl r5,r6,0x1
lsl r3,r6,0x11
lsr r3,r3,0x11
ldr r1,[r7,0x4]			; Source Address
ldr r2,[r7,0x10]		; Destination Address 2
mov r8, r1

ldr r0,=0x040000D4
str r1,[r0]
add r0, #0x4
str r2,[r0]
add r0, #0x4
mov r1, #0x80
lsl r1, r1, 0x18
orr r1, r1, r3
str r1,[r0]
ldr r1,[r0]

mov r1, r8
add r2,r2,r5
str r2,[r7,0x10]
add r1,r1,r5
str r1,[r7,0x4]

decompress_end:
ldrh r0,[r7]
add r5,r0,0x1
strh r5,[r7]
ldrh r1,[r7,0x2]

lsl r0, r5, 0x10
lsr r0, r0, 0x10
cmp r0,r1
bcc decompress_start

; Copia a imagem para a VRAM
ldr r1,=image_address + 0x400
mov r2, #0x06000000
mov r3, #0x6000
ldr r0,=0x040000D4
str r1,[r0]
add r0, #0x4
str r2,[r0]
add r0, #0x4
mov r1, #0x80
lsl r1, r1, 0x18
orr r1, r1, r3
str r1,[r0]
ldr r1,[r0]

ldr r1,=image_address + 0x400 + 0xC000
mov r2, #0x06200000
mov r3, #0x6000
ldr r0,=0x040000D4
str r1,[r0]
add r0, #0x4
str r2,[r0]
add r0, #0x4
mov r1, #0x80
lsl r1, r1, 0x18
orr r1, r1, r3
str r1,[r0]
ldr r1,[r0]

mov r9, #0x20	; Tempo de espera, em "atualizações de tela"
mov r10, #0x2

ldr r1,=image_address
ldr r4,=image_address
mov r2, #0x05000000
orr r8, r2, #0x400
mov r3, #0x0
in_set:
mov r6, 0x0
ldrh r7,[r1]
ldrh r5,[r4]
strh r7,[r2]
strh r5,[r8]
add r2, r2, 0x2
add r8, r8, 0x2
add r1, r1, 0x2
add r4, r4, 0x2
add r3, r3, 0x2
cmp r3, #0x200
bcc in_set

fade_in:
ldr r0,=0x4000214	; IF
ldr r5,=0x4000130
ldr r7,=0x3ff

in_loop:
ldrh r6,[r5]
cmp r6,r7
bne clear
ldr r2,[r0]
str r2,[r0]
tst r2,#0x1 ; Espera a flag VBlank ser setada
beq in_loop
subs r10, r10, #0x1
bne in_loop

subs r9, r9, #0x1
mov r10, #0x20
sub r10,r9
;lsr r2,r10,1
lsr r2,r9,1
orr r2,0x8000
ldr r1,=0x400006c
str r2,[r1]
ldr r1,=0x400106c
str r2,[r1]
mov r10, #0x2
bne fade_in

; WAIT estático
mov r1, #0x90	; Tempo de espera, em "atualizações de tela"
ldr r0,=0x4000214	; IF
ldr r5,=0x4000130
ldr r7,=0x3ff

wait_loop:
ldrh r6,[r5]
cmp r6,r7
bne clear
ldr r2,[r0]
str r2,[r0]
tst r2,#0x1 ; Espera a flag VBlank ser setada
beq wait_loop
subs r1, r1, #0x1
bne wait_loop

mov r9, #0x20	; Tempo de espera, em "atualizações de tela"
mov r10, #0x2

fade_out:
ldr r0,=0x4000214	; IF
ldr r5,=0x4000130
ldr r7,=0x3ff

out_loop:
ldrh r6,[r5]
cmp r6,r7
bne clear
ldr r2,[r0]
str r2,[r0]
tst r2,#0x1 ; Espera a flag VBlank ser setada
beq out_loop
subs r10, r10, #0x1
bne out_loop

subs r9, r9, #0x1
mov r10, #0x20
sub r10,r9
lsr r2,r10,1
orr r2,0x8000
ldr r1,=0x400006c
str r2,[r1]
ldr r1,=0x400106c
str r2,[r1]
mov r10, #0x2
bne fade_out


clear:
mov r12, 0x4000000
b 0x2000804

.pool

credits_image:
.import "splash_c.bin"
  

.close

