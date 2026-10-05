/* func_002d0c10 : 空壳栈帧包装（o1_jal，编译档 -O1）
 * 由 routebjp/tools/auto_match_wrapper.py 生成；objdiff 100% 后纳入 hybrid。
 * 语义：本函数只做参数整理后调用 func_002d1c38（延迟槽/nop 由模板决定）。 */
extern void func_002d1c38();

void func_002d0c10() { func_002d1c38(); }
