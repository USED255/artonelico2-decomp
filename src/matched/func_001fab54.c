/* func_001fab54 : 空壳栈帧包装（o1_jal，编译档 -O1）
 * 由 routebjp/tools/auto_match_wrapper.py 生成；objdiff 100% 后纳入 hybrid。
 * 语义：本函数只做参数整理后调用 func_001f9ffc（延迟槽/nop 由模板决定）。 */
extern void func_001f9ffc();

void func_001fab54() { func_001f9ffc(); }
