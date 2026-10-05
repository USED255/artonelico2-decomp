#!/usr/bin/env python3
"""按「拼接全部 PT_LOAD 段」的口径抽取 ELF 载荷（路线 B 棘轮口径）。

美版是单 PT_LOAD，日版是**两个** PT_LOAD（中间 vram 有 0x80 空洞）。
用 `objcopy -O binary` 会把两段之间的 0x80 空洞也补进输出（9,305,064 B），
与原版拼接口径（9,304,936 B）不符；所以这里直接读程序头拼接。

用法: python3 extract_payload.py <elf> <out.bin>
输出: 打印 "size sha1 path"
"""
import hashlib
import struct
import sys


def main():
    elf, out = sys.argv[1], sys.argv[2]
    d = open(elf, "rb").read()
    e_phoff, e_phentsize, e_phnum = struct.unpack_from("<I", d, 28)[0], \
        struct.unpack_from("<H", d, 42)[0], struct.unpack_from("<H", d, 44)[0]
    payload = b""
    segs = []
    for i in range(e_phnum):
        t, off, va, pa, fsz, msz, fl, al = struct.unpack_from("<IIIIIIII", d, e_phoff + i * 32)
        if t == 1:
            payload += d[off:off + fsz]
            segs.append((off, va, fsz, msz, fl))
    open(out, "wb").write(payload)
    print("PT_LOAD 段数 = %d" % len(segs))
    for off, va, fsz, msz, fl in segs:
        print("   off=0x%06x va=0x%08x filesz=0x%x memsz=0x%x flags=%d" % (off, va, fsz, msz, fl))
    print("%d %s %s" % (len(payload), hashlib.sha1(payload).hexdigest(), out))
    print("md5 = %s" % hashlib.md5(payload).hexdigest())


if __name__ == "__main__":
    main()
