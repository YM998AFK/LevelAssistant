# 物件 Prefab 元数据 (object_prefab_meta)

> 自动由 [scripts/build_object_prefab_meta.py](../../../scripts/build_object_prefab_meta.py) 生成。
> 数据源：
> - prefab: `D:/meishu/Assets/BundleResources/ide/sprite3d/*.prefab`
> - controller: `D:/meishu/Assets/BundleResources/model/**/*.controller`
> - animation clip: `*.fbx.meta` 里 `clipAnimations` 段（firstFrame/lastFrame/loopTime）
> - material/texture: `*.mat` → `_MainTex/_BaseMap` guid → 贴图文件

## 命中率

- asset_catalog 物件行：**1065**
- 在美术目录找到 prefab：**1064**（缺 1）
- AnimatorState 总数 1042，其中 loop/duration 命中 **569**（其余 FBX.meta 为 legacy 模式不含 clip 元数据）
- 成功追溯 material 的物件：**792** / 成功追溯 texture 的：**778**

## 字段说明

- **Collider**：真实物理碰撞体（Box/Sphere/Capsule/Mesh），尺寸来自 prefab 源头，不受 .ws 里 Size/Scale 覆盖。
  - Box → `m_Size`；Sphere → `r=`；Capsule → `r=/h=`；`Trigger` 代表可穿过
- **轴心偏移**：
  - `轴心在底部`：center.y ≈ size.y/2 → 摆放时直接 `Position.y = 地面` 即可
  - `轴心居中`：center ≈ 0 → 摆地上要抬 size.y/2
  - 其它 → 需手动核对
- **渲染/能力**：静态×N / 蒙皮×N / 粒子×N / 光源×N / 音源×N
- **动画**：`state名(时长s,循环|一次)`；时长按 30fps 推算。缺 loop/duration 的是 FBX.meta 未配置 clipAnimations（legacy 模式）。
- **默认 Scale**：prefab 根 Transform m_LocalScale（多数 1，个别放大）。
- **子GO**：prefab 内 GameObject 总数 - 1。
- **特殊脚本**：pangu 引擎 MonoBehaviour（目前识别 MeshPartSettings）。

## 主表：物件元数据

| AssetId | 名称 | prefab | Collider | 轴心偏移 | 渲染/能力 | Animator clip (时长/循环) | 默认Scale | 子GO | 特殊脚本 |
|---------|------|--------|----------|----------|-----------|---------------------------|-----------|------|----------|
| 10043 | 空盒子 | blockout1MX1M.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | MeshPartSettings |
| 10167 | 立体路径 | grids.prefab | Box [1, 1, 1] | [0, 0.5, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | MeshPartSettings |
| 10548 | 空挂点 | empty.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | MeshPartSettings |
| 12391 | 煤球道具 | meiqiu.prefab | Box [0.8, 0.7, 0.74] | [0.01, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 12392 | 金蛋道具 | jindan.prefab | Box [1.09, 0.69, 0.85] | [-0.05, 0.35, 0.18] (轴心在底部) | - | - | [3.12, 3.12, 3.12] | 0 | - |
| 12395 | 腰牌 | lingpai.prefab | Box [0.58, 0.13, 0.87] | [0.01, 0.07, 0.12] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 12396 | 账本 | zhangben.prefab | Box [0.66, 0.2, 0.88] | [0.01, -0.03, -0.47] (轴心居中) | - | - | [1, 1, 1] | 1 | - |
| 12582 | 宝箱 | baoxiang.prefab | Box [0.53, 0.45, 0.42] (+1个) | [-0, 0.24, 0] (轴心在底部) | 蒙皮×1 / 静态×1 | open(2.33s,一次), guan(0.67s,循环), kai | [1, 1, 1] | 5 | - |
| 12583 | 领奖台 | jianglitai.prefab | Box [4.55, 2.87, 5.91] | [0.06, 0.93, -0.01] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 12584 | 滑草鞋 | huacaoxie.prefab | Box [1.31, 1.04, 1] | [0.03, 0.52, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 12585 | 九婴攻略 | gongnue.prefab | Box [0.66, 0.2, 0.88] | [0.01, -0.03, -0.47] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 12586 | 钥匙 | dujingyaoshi.prefab | Box [1.78, 1.15, 1] (+1个) | [0.05, 0.06, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 12587 | 神羽 | yumao.prefab | Box [1.25, 1.35, 0.28] | [-0.23, 0.45, 0.06] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 12588 | 普通机械螃蟹 | pangxie.prefab | Capsule r=0.5,h=1.19 (+1个) | [0, 0.53, 0] | 静态×1 | idle(1.60s,循环), xiangshangzou, fennu, kaixin, shoushang, daji, xiuli, idle_shoushang(1.60s,循环), walk(1.00s,循环), xiangxiazou | [1, 1, 1] | 2 | - |
| 12630 | 五彩神羽 | caiseyumao.prefab | Box [1.52, 1.37, 0.34] | [0.01, 0.57, 0.03] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 12945 | 九婴体内牌子 | paizi.prefab | Box [1.1, 0.92, 0.1] | [0, 0.46, 0] (轴心在底部) | 静态×1 | - | [2.47, 2.28, 2.47] | 0 | - |
| 12946 | 九婴体内-红灯 | light-r.prefab | Box [1, 0.35, 1] | [0, 0.16, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 12947 | 九婴体内-绿灯 | light-g.prefab | Box [1, 0.35, 1] | [0, 0.16, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13007 | 一片草丛 | sm_cao.prefab | Box [1, 0.6, 0.46] | [-1.1, 0.3, 0.09] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 13009 | 书 | sm_book.prefab | Box [0.3, 0.14, 0.34] | [-0, 0.07, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13010 | 分流机器 | sm_fenliujiqi.prefab | Box [2.13, 1.49, 3.14] | [0, 0.72, 0.48] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13011 | 评级机器02 | sm_pingjijiqi_b.prefab | Box [0.73, 0.42, 2.27] | [0, 0.2, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13012 | 食人花 | sm_rafflesia.prefab | Box [0.85, 1.03, 0.73] | [0, 0.48, 0.08] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13013 | 钥匙 | sm_yaoshi.prefab | Box [0.14, 0.26, 0.06] | [0, 0.12, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13014 | 锻造材料01 | sm_lianzaocailiao_01.prefab | Box [1.3, 1.3, 1.3] | [0, 0.64, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13015 | 锻造材料02 | sm_lianzaocailiao_02.prefab | Box [1.3, 1.2, 1.3] | [0, 0.59, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13016 | 锻造材料03 | sm_lianzaocailiao_03.prefab | Box [1.3, 1.3, 1.3] | [0, 0.61, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13017 | 一篮煤球 | sm_yilanmeiqiu.prefab | Box [1.3, 1.21, 1.28] | [0, 0.59, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13310 | 分流机器01 | sm_fenliujiqi_a.prefab | Box [1.93, 1.44, 2.02] | [0, 0.72, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13311 | 分流机器02 | sm_fenliujiqi_b.prefab | Box [0.42, 0.27, 1.75] | [0, 0.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13313 | 评级机器 | sm_pingjijiqi.prefab | Box [3.07, 2.83, 3.97] | [0, 1.29, 0.59] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13323 | 天雷殿图册 | sm_shu_01.prefab | Box [0.42, 0.18, 0.59] | [0, 0.04, -0.01] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 13328 | 一袋金币 | sm_qiandai.prefab | Box [0.34, 0.38, 0.28] | [-0.05, 0.19, 0.03] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13329 | 雷神之锤 | sm_leishenzhichui.prefab | Box [0.37, 0.5, 0.32] | [0.02, 0.26, -0.02] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13330 | 蜻蜓之翼 | sm_zhuqingting.prefab | Box [0.63, 0.47, 0.24] | [0.03, 0.18, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13344 | 桌子 | sm_tavern_zhuozi.prefab | Box [10, 2, 4.9] | [0, 0.96, 0.17] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 13355 | 殿内石柱 | sm_zhuzi.prefab | Box [2.01, 8.15, 1.92] | [0, 4.04, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13359 | 壁画1—代码化 | sm_bihua_01.prefab | Box [4.14, 2.76, 1] | [0.04, 1.44, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13360 | 壁画2—代码化 | sm_bihua_02.prefab | Box [4.2, 3.09, 0.51] | [-0.35, 1.41, 0.04] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 13363 | 石台 | sm_shitai.prefab | Box [1.49, 1.75, 1.85] Trigger | [0, 0.72, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 14511 | 黄牛铁链 | sm_tielian.prefab | Box [4.1, 1.6, 3.32] | [-0.25, 0.24, 0.4] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 14515 | 灌溉车 | sm_guoshanche.prefab | Box [13.72, 4.62, 4.53] | [-5.7, 2.13, -0.64] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 14516 | 茶杯展示架 | sm_jiazi.prefab | Box [4.97, 2.86, 1.32] | [0, 1.43, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14517 | 海茉莉 | sm_haitanghua_01.prefab | Box [0.67, 0.86, 0.57] | [0, 0.43, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14518 | 陷阱 | sm_traps_01.prefab | Box [1.24, 0.65, 1.44] | [-0, 0.33, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14519 | 红外遥控器 | sm_yaokongqi.prefab | Box [0.18, 0.43, 0.06] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14520 | 智慧小屋02 | sm_zhihui_03.prefab | Box [-7.17, -6.36, 3.97] | [0.36, 3.03, -0.05] | - | - | [1, 1, 1] | 0 | - |
| 14640 | 蜜雪冰牛奶茶粉 | sm_mixuebingniu_fen.prefab | Box [0.35, 0.66, 0.31] Trigger | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14641 | 蜜雪冰牛奶茶黄 | sm_mixuebingniu_huang.prefab | Box [0.35, 0.66, 0.31] Trigger (+1个) | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14642 | 蜜雪冰牛奶茶蓝 | sm_mixuebingniu_lan.prefab | Box [0.35, 0.66, 0.31] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14643 | 蜜雪冰牛奶茶绿 | sm_mixuebingniu_lv.prefab | Box [0.35, 0.66, 0.31] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14644 | 棍棒 | sm_langyabang.prefab | Box [0.49, 1.7, 0.43] Trigger | [0, 0.85, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14645 | 草叉 | sm_yucha.prefab | Box [0.93, 3.12, 0.19] Trigger | [0, 1.56, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14646 | 马桶撅 | sm_matongsai.prefab | Box [0.84, 1.85, 0.84] Trigger | [0, 0.92, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14647 | 木牌 | sm_lupai.prefab | Box [2.19, 2.02, 0.28] | [-0.09, 1.01, -0.06] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14648 | 桌子 | sm_zhuozi.prefab | Box [1.74, 1.06, 1.74] | [-0, 0.53, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14649 | 昆仑灵芝 | sm_lingzhi_01.prefab | Box [0.7, 0.46, 0.51] Trigger | [-0, 0.23, -0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14651 | 天山雪莲 | sm_lianhua.prefab | Box [1.35, 0.67, 1.36] Trigger | [-0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14652 | 特制炼丹鼎 | sm_ding.prefab | Box [3.68, 2.24, 2.64] Trigger | [0, 1.12, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14653 | 九转还魂丹 | sm_qiu.prefab | Box [0.66, 0.65, 0.63] Trigger | [-0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14654 | 珍珠竹筐 | sm_zhukuang_zhenzhu.prefab | Box [0.68, 0.78, 0.88] | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14655 | 红豆竹筐 | sm_zhukuang_hongdou.prefab | Box [0.68, 0.78, 0.88] Trigger | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14656 | 椰果竹筐 | sm_zhukuang_yeye.prefab | Box [0.68, 0.78, 0.88] | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14668 | 海州衙门桌子 | sm_haizhouyamen_zhuozi.prefab | Box [2.19, 1.84, 1.32] Trigger | [0, 0.92, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14670 | 绿桌子 | sm_zhuozi_lv.prefab | Box [1.74, 1.06, 1.74] | [-0, 0.53, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14671 | 被污染的昆仑灵芝 | sm_wuranlingzhi.prefab | Box [0.7, 0.46, 0.51] Trigger | [0, 0.23, -0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14677 | 八面玲珑眼 | sm_daoju_maoleida.prefab | Box [1, 1, 1] | [0, 0.43, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 14680 | 猫雷达 | maoleida.prefab | Box [0.5, 0.5, 0.5] (+1个) | [0, 0.22, 0] (轴心在底部) | 静态×1 | leidachuxian(1.17s,一次), leidadaiji(1.00s,一次), idle(0.56s,循环), hongdiandaiji | [1, 1, 1] | 2 | - |
| 14720 | 核桃飞机_3D | hetaofeiji_3D.prefab | Capsule r=0.5,h=6.43 | [0, 0.15, 0] | - | fly | [1, 1, 1] | 0 | - |
| 14721 | 黄牛_3D | huangniu_3D.prefab | Capsule r=0.68,h=2.9 (+1个) | [0, 1.46, 0] | 静态×1 | fangentou_loop(0.60s,循环), jinzhang, taodongxi, wanyaojiandongxi, nanguo, dianzan, run(0.80s,循环), zihao, dianji, idle(1.60s,循环), sikao, fangentou_end(0.40s,一次), haipa, zhengzha(2.50s,循环), tiaoqi, dazhaohu, jingya, fangentou_start(0.13s,一次), shouwuzudao, chayao, daoxia, xiaoshengshuohua, lanyao, xiaodonghua02, naotou, kuzhetouxiang, fennu, wuyu, bixinwu, daoxiaxunhuan(1.67s,循环), xiaodonghua, chuanqi(2.00s,循环), shengqiduojiao, dakeshui(2.00s,循环), toutoushuohua, daxiao, idle_jingya(1.60s,循环), xingfenjidong, beibang(1.60s,循环), walk(1.20s,循环), ku, wuduzi, zhi | [1, 1, 1] | 3 | 其它脚本×1 |
| 14722 | 队长_3D | nanhai_3D.prefab | Capsule r=0.5,h=2.28 (+1个) | [0, 1.03, 0] | 静态×1 | nanguo, zhenjing, lanyao, xiaodonghua, run(0.80s,循环), xiaoshengshuohua, xingfen, jinzhang, sikao, walk(1.07s,循环), wuer, zihao, taolingpai, taodongxi, tanshou, haipa, naotou, shengqi, idle(1.60s,循环), daxiao, xiaodonghua2, zuo_idle(1.60s,循环), dazhaohu, wanyaowuduzi, wuyu, wanyaojiandongxi | [1, 1, 1] | 4 | 其它脚本×2 |
| 14723 | 展喵_3D | zhanmiao_3D.prefab | Capsule r=0.5,h=2.51 (+1个) | [0, 1.25, 0] | 静态×1 | bengkuibaotou, run(0.80s,循环), qienuo_xuanyun(1.60s,循环), xusheng(2.17s,循环), haipaliulei, xuruo_loop(1.60s,循环), wuyu, idle02(1.60s,循环), wanyaowuduzi, dahan, idle(1.60s,循环), dazhaohu, zhenjing, rengshitou, ganga, baoxiong, huidao, xiaodonghua2, yansu, nanguo, beixi(0.53s,循环), jinzhang, xiayitiao, paochucanying, walk(1.07s,循环), jump, yihuo, qienuo_idle(1.60s,循环), zuoyi, zhizheqianfang, qienuo_huidao, daxiao, haipa, lanyao, yundao_loop, naotou, xingfenjidong, zihao, shengqi, sikao, wanyaojiandongxi, chuanqi(2.00s,循环), dianzan(1.83s,一次), badao, xiaodonghua | [1, 1, 1] | 5 | 其它脚本×1 |
| 14724 | 小核桃_3D | xiaohetao02_3D.prefab | Capsule r=0.5,h=1.97 (+1个) | [0, 0.93, 0] | 静态×1 | bianshenfeiji, jiguangpao, idle(1.73s,循环), run(0.67s,循环), dazhaohu, danshoubeng(2.27s,循环), walk(1.07s,循环), daoli_run(0.40s,循环), chongneng02, yundao, lingguangyishan02, naotou02, jingxia(2.00s,一次), haipa, jingzhang, sleep_strat(1.07s,一次), walk2, naotou, dianjishoubi02, jiebang, shengqiduojiao, sikao02, wuduzi, lanyao02, yundao_shuijiao(1.33s,循环), xingfenjidong, kuangxiao, daoli_idle(1.73s,循环), rouyan, zuoyi, wuyu, daxiao, chongneng, saomiao, bianshen02, danxiguidi(1.60s,循环), haipabaotou, wanyaokaixiang, run2, zhi02, sikao, taishou_end(0.37s,一次), jiandongxi, idle01, beixi(0.67s,循环), changge, xiaoshengshuohua, nanguo, gangawulian, zihao, xiaodonghua, weiyao, "\u8F6C\u5934\u5C0F\u58F0\u8BF4\u8BDD", dichudongxi, bianshen, lanyao, zhi, taishou(0.97s,一次), wuyu02, taishou_loop(1.00s,循环), zuo_idle(1.73s,循环), sleep(1.33s,循环), dangfeng(1.73s,循环), kaixin, chuanqi(2.00s,循环), xiaodonghua2, beibang, kanxianshiping(1.73s,循环) | [1, 1, 1] | 5 | 其它脚本×1 |
| 14725 | 核桃机甲_3D | hetaojijia_3D.prefab | Capsule r=0.5,h=5.18 (+1个) | [0, 2.45, 0] | 静态×1 | run(0.80s,循环), gui_idle(1.33s,循环), saomiao, zhuanshen, dianchidun, qifei, beifengchui, jump, dianchidun_idle(1.33s,循环), jianyaopai, fashe, idle(1.60s,循环), walk(1.33s,循环), tuiguangbo(1.73s,循环) | [1, 1, 1] | 4 | - |
| 14727 | 茶杯盖子 | chabeigaizi.prefab | Box [1, 0.65, 1] (+1个) | [0, 0.27, 0] (轴心在底部) | 静态×1 | idle(1.07s,循环), walk(1.00s,循环), gaizhu(1.07s,循环) | [1, 1, 1] | 2 | - |
| 14728 | 金光宝石（正常状态） | sm_l3_jinguangbaoshi_01.prefab | Box [0.21, 0.3, 0.13] | [0, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14729 | 金光宝石（强光状态） | sm_l3_jinguangbaoshi_02.prefab | Box [0.21, 0.3, 0.13] | [0, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14730 | 海蓝宝石（正常状态） | sm_l3_hainanbaoshi_01.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14731 | 海蓝宝石（强光状态） | sm_l3_hainanbaoshi_02.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14732 | 鉴宝机 | sm_l3_jianbaoji.prefab | Box [2.59, 2.8, 2.12] Trigger | [-0, 1.4, -0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14733 | 龟壳打印机01 | sm_l3_wuguidayinji_01.prefab | Box [1.45, 0.7, 1.8] | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14734 | 龟壳打印机02 | sm_l3_wuguidayinji_02.prefab | Box [1.45, 0.7, 1.8] | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14735 | 龟壳打印机03 | sm_l3_wuguidayinji_03.prefab | Box [1.45, 0.7, 1.8] | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14736 | 龟壳打印机04 | sm_l3_wuguidayinji_04.prefab | Box [1.45, 0.7, 1.8] | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14737 | 景王喂食机1号 | sm_l3_jiingwangweishiji_01.prefab | Box [0.86, 0.65, 0.93] | [0, 0.33, 0.09] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14738 | 景王喂食机2号 | sm_l3_jiingwangweishiji_02.prefab | Box [0.86, 0.65, 0.93] | [0, 0.33, 0.09] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14739 | 景王种植机 | sm_l3_zhongzhiji.prefab | Box [1.46, 1.32, 0.95] | [0, 0.66, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14758 | 破船 | sm_l3_pochuan.prefab | Box [7.57, 5.26, 3.03] Trigger | [-0.14, 2.71, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 14759 | 好船 | sm_l3_haochuan_01.prefab | Box [18.32, 7.87, 7.41] (+1个) | [-0.3, 3.83, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 14761 | 密室大门 | sm_l3_mimasuo_damen.prefab | Box [6.52, 3.75, 0.62] Trigger | [0, 1.88, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15073 | 密室大门-2 | sm_mimasuodameng_02.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 15074 | 密码锁1 | sm_l3_mimasuo_06.prefab | Box [4.62, 1.25, 0.19] Trigger | [0, 0.63, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15075 | 密码锁2 | sm_l3_mimasuo_05.prefab | Box [4.62, 1.24, 0.19] Trigger | [-0.01, 0.62, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15076 | 密码锁3 | sm_l3_mimasuo_07.prefab | Box [4.62, 1.27, 0.19] Trigger | [0, 0.63, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15077 | 密码锁4 | sm_l3_mimasuo_08.prefab | Box [4.62, 1.25, 0.19] Trigger | [0, 0.63, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15078 | 密码锁（源代码化） | sm_mimasuo.prefab | Box [4.62, 1.21, 0.19] Trigger (+3个) | [-0.01, 0.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 4 | - |
| 15079 | 清道夫 | sm_l3_qingdaofu.prefab | Box [1.46, 1.61, 0.86] Trigger | [0, 0.8, -0.04] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 15080 | 水瓶 | sm_l3_shuiping.prefab | Box [0.42, 0.43, 0.29] Trigger | [-0.07, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15081 | 神秘宝石 （机关球） | sm_l3_shenmibaoshi.prefab | Box [0.39, 0.39, 0.39] Trigger | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15082 | 碎布 | sm_l3_suibu.prefab | Box [0.35, 0.4, 0.04] Trigger | [0, 0.2, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15188 | 智慧核心 | zhihuihexin.prefab | Box [2.1, 1.75, 0.75] (+1个) | [0, 0.88, 0] (轴心在底部) | 蒙皮×4 / 静态×1 | lptupian, huanying, hpidle, lpwenzi | [1, 1, 1] | 12 | - |
| 15189 | 秋生账本 | sm_l3_qiushegnzhangben.prefab | Box [0.55, 0.08, 0.53] Trigger | [0, 0.04, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15285 | 自动投喂机 | sm_l3_jiingwangweishiji_po.prefab | Box [0.86, 0.68, 0.93] Trigger | [0, 0.34, 0.09] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15286 | 密码手册 | sm_l3_mimashouce.prefab | Box [0.93, 0.09, 0.44] Trigger | [-0, 0.04, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 15863 | 自动投喂机说明书 | sm_l3_shuomingshu.prefab | Box [0.35, 0.04, 0.56] Trigger | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16086 | 蒙汗药01 | sm_kejianbuji_menghanyao_01.prefab | Box [0.8, 0.21, 0.78] Trigger | [0, 0.09, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16087 | 蒙汗药02 | sm_kejianbuji_menghanyao_02.prefab | Box [3.16, 0.56, 3.31] Trigger | [0, 0.28, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16090 | l4门 | l4_gsgc_men.prefab | Box [8.5, 9.5, 2] | [0, 4.5, 0] (轴心在底部) | - | kaimenidle(3.33s,循环), kaimen, idle(3.33s,循环) | [1, 1, 1] | 0 | - |
| 16356 | 水池盖子 | shuichigaizidu01.prefab | Box [23, 1, 9] | [0, 0.15, 0] (轴心偏移) | - | yidong, idle(0.07s,循环) | [1, 1, 1] | 1 | - |
| 16363 | 防虫栅栏 | sm_l4_hulan_01.prefab | Box [1.1, 2.24, 6.13] | [0, 1.12, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16382 | 金字塔 | sm_l4_jinzita.prefab | Box [0.59, 0.56, 3.37] Trigger (+16个) | [0, 0.28, 0] (轴心在底部) | - | - | [1, 1, 1] | 15 | - |
| 16383 | 虎身人面像 | sm_l4_baihu.prefab | Box [1.66, 2.09, 3.36] Trigger | [0, 1, -0.17] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 16384 | pad | sm_l4_pad.prefab | Box [0.86, 0.66, 0.17] Trigger | [-0.01, 0.32, -0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 16385 | 蒸汽宝典 | sm_l4_zhengqibaodian.prefab | Box [2.19, 1.41, 0.51] Trigger (+1个) | [0, 0.7, 0.05] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 16386 | 进化芯片中 | sm_l4_jinhuaxinpian_02.prefab | Box [0.74, 0.54, 0.18] Trigger | [0, 0.27, 0.06] (轴心在底部) | 静态×2 | - | [1.77, 1.77, 1.77] | 2 | - |
| 16387 | 进化芯片小 | sm_l4_jinhuaxinpian.prefab | Box [0.74, 0.54, 0.18] Trigger | [0, 0.27, 0.06] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 16388 | 兴奋薄荷的能量果实车 | sm_l4_daoju_qiche_04.prefab | Box [3.99, 3.18, 6.87] Trigger | [0, 1.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16389 | 白菜的能量果实车 | sm_l4_daoju_qiche_05.prefab | Box [3.99, 3.18, 6.87] Trigger | [0, 1.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16390 | 生命萝卜的能量果实车 | sm_l4_daoju_qiche_01.prefab | Box [3.99, 3.18, 6.87] Trigger | [0, 1.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16391 | 防御椰子能量果实车 | sm_l4_daoju_qiche_03.prefab | Box [3.99, 3.18, 6.87] Trigger | [0, 1.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16392 | 敏捷香蕉能量果实车 | sm_l4_daoju_qiche_02.prefab | Box [3.99, 3.18, 6.87] Trigger | [0, 1.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16393 | 葫芦能量果实车 | sm_l4_daoju_qiche_06.prefab | Box [3.99, 3.18, 6.87] (+10个) | [0, 1.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 10 | - |
| 16394 | 能源矿车 | sm_l4_daoju_chexiang.prefab | Box [2.51, 1.33, 1.67] Trigger | [0, 0.67, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16395 | 躺平西瓜 | sm_l4_bindongxigua.prefab | Box [0.91, 0.95, 0.83] Trigger | [0, 0.49, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16396 | 碎石1 | sm_l4_suishi_01.prefab | Box [2.83, 1.22, 2.21] Trigger | [0, 0.61, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16397 | 碎石2 | sm_l4_suishi_02.prefab | Box [1.68, 0.58, 1.59] Trigger | [0, 0.29, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16398 | 碎石3 | sm_l4_suishi_03.prefab | Box [0.87, 0.33, 0.86] Trigger | [0, 0.17, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16399 | 木牌子 | sm_l4_mupai.prefab | Box [2.19, 2.02, 0.26] Trigger | [-0.09, 1.01, -0.05] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16400 | 梼杌（曾用名貔貅）大脚 | sm_l4_dajiao.prefab | Box [2.59, 7.65, 4.67] Trigger | [0, 3.82, 0.43] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16401 | 梼杌（曾用名貔貅）大头 | sm_l4_datou.prefab | Box [6.39, 7.69, 9.5] Trigger | [0, 4.01, 1.56] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16402 | 冰块碎石1 | sm_l4_suibing_01.prefab | Box [0.62, 1.01, 0.4] Trigger | [0, 0.5, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16403 | 冰块碎石2 | sm_l4_suibing_02.prefab | Box [0.96, 0.71, 0.51] Trigger | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16404 | 冰块碎石3 | sm_l4_suibing_03.prefab | Box [0.71, 0.72, 0.51] Trigger | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16405 | 冰块碎石4 | sm_l4_suibing_04.prefab | Box [0.41, 1.25, 0.42] Trigger | [0, 0.62, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16406 | 红温保安 | gongchanganbao_hongwen.prefab | Capsule r=1,h=3 (+1个) | [0, 1.5, 0] | 静态×1 | idle(1.60s,循环), walk(1.07s,循环), run(0.60s,循环) | [1, 1, 1] | 2 | - |
| 16407 | 红温食人花 | shirenhua_hongwen.prefab | Box [1, 1.6, 1] (+1个) | [0, 0.77, 0] (轴心在底部) | 静态×1 | fengkuangyaobai(0.53s,循环), bizuihujiu(1.33s,循环), bizuiidle(1.33s,循环), zhangzuiidle(1.33s,循环), yao(1.00s,一次) | [1, 1, 1] | 2 | - |
| 16408 | 红温扫地鲲 | saodikun_hongwen.prefab | Capsule r=2,h=1.7 (+1个) | [0, 2.7, 0] | 静态×1 | zhangzuichutizi, jiangzhi_start(1.67s,一次), zhangzuidaiji(1.60s,循环), tiaowu, jiangzhi_end(1.40s,一次), idle(1.60s,循环), run(0.67s,循环), beishang, kaixing, walk(1.07s,循环), jiangzhi_idle(1.33s,循环), shoutizi(1.97s,一次) | [1, 1, 1] | 2 | - |
| 16409 | 红温机械狗仔 | jixiegouzhaiV01_hongwen.prefab | Capsule r=0.5,h=1.6 (+1个) | [0, 0.75, 0] | 静态×1 | run(0.53s,循环), walk(1.07s,循环), idle(1.60s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 16410 | 红温螃蟹 | pangxie_hongwen.prefab | Capsule r=0.5,h=1.19 (+3个) | [0, 0.53, 0] | 静态×1 | idle(1.60s,循环), xiangshangzou, fennu, kaixin, shoushang, daji, xiuli, idle_shoushang(1.60s,循环), walk(1.00s,循环), xiangxiazou | [1, 1, 1] | 3 | - |
| 16411 | 朱雀 | zhuque.prefab | Capsule r=1,h=3.5 (+1个) | [0, 1.65, 0] | 静态×1 | kaixing(1.33s,循环), tiedi_walk(1.07s,循环), zhanli_idle(1.60s,循环), idle(1.30s,循环), walk(1.03s,循环), daku(1.33s,循环), run(0.67s,循环), paidachibang | [1, 1, 1] | 4 | 其它脚本×1 |
| 16412 | 青龙 | sm_l4_qinglong.prefab | Box [1, 1, 1] Trigger | [0, 0, 0] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 16413 | 白虎 | baihu.prefab | Capsule r=0.7,h=2.5 (+2个) | [0, 1.2, 0] | 静态×1 | yihuo, idle(1.60s,循环), zhongdan, gongji, run(0.53s,循环), pufuqiuren, walk(1.07s,循环), tangdi, suxing, yaobai | [1, 1, 1] | 5 | 其它脚本×2 |
| 16416 | 条幅 | sm_l4_hengfu_01.prefab | Box [6.63, 1.07, 0.08] Trigger | [0, 0.53, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16417 | 纸张1 | sm_l4_feizhi_01.prefab | Box [0.38, 0, 0.44] Trigger | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16418 | 纸张2 | sm_l4_feizhi_02.prefab | Box [0.3, 0, 0.4] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16419 | 毛笔 | sm_l4_maobi_01.prefab | Box [0.05, 0.46, 0.05] Trigger | [0, 0.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16420 | 一堆小甜辣薄荷 | sm_l4_daoju_hua_01.prefab | Box [2.03, 1, 1.82] | [-0.33, 0.17, -0.01] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 16421 | 一堆大甜辣薄荷 | sm_l4_daoju_hua_02.prefab | Box [4.17, 1, 3.66] | [0.07, 0.08, -0.19] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 16422 | 冰冻白菜 | sm_l4_bingdongbaicai.prefab | Box [1.02, 0.81, 0.16] | [0, 0.42, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16423 | 芒果派 | sm_l4_mangguopai.prefab | Box [0.51, 0.22, 0.52] | [0, 0.11, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16424 | 石头路灯 | sm_l4_daoju_shideng.prefab | Box [1.72, 2.45, 1.16] | [0, 1.2, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 16425 | 灯珠 | sm_l4_daoju_dengpai.prefab | Box [0.52, 3.5, 0.09] | [-0.01, 1.76, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16427 | 算盘 | sm_l5_shanyangsuanpan.prefab | Box [2.71, 0.22, 1.55] | [0, 0.08, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16428 | 圣旨 | sm_l5_shengzhi.prefab | Box [0.6, 0.66, 1.02] | [-0.14, 0.18, 0.55] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16433 | 破烂喵朝军营帐篷 | sm_l5_hdzk_jianzhu_03_po.prefab | Box [11.88, 6.51, 13.54] | [0, 3.25, -0.1] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16437 | 降维陨石 | sm_l4_shibei_01.prefab | Box [3.19, 6.55, 0.89] | [0, 3.28, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16455 | 地图碎片3 | sm_ditusuipian_03.prefab | Box [1.12, 1.74, 0.01] Trigger | [0, 0.86, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16456 | 地图碎片2 | sm_ditusuipian_02.prefab | Box [1.12, 1.74, 0.01] Trigger | [0, 0.86, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16457 | 地图碎片1 | sm_ditusuipian_01.prefab | Box [1.12, 1.74, 0.01] Trigger | [0, 0.86, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16458 | 桃源山全图 | sm_ditusuipian.prefab | Box [1.12, 1.74, 0.01] Trigger (+2个) | [0, 0.86, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 2 | - |
| 16599 | 闸门开关 | zhamenkaiguan.prefab | Box [3.2, 2.2, 1.5] | [0, 1.15, 0] (轴心在底部) | - | zhamenkaiguan_dakai(0.53s,一次), zhamenkaiguan_dakaidaiji(0.03s,一次), zhamenkaiguan_idle(0.07s,一次) | [1, 1, 1] | 0 | - |
| 16956 | 星座壁画 | sm_l4_xingzuobihua.prefab | Box [7.72, 6.96, 3.16] Trigger | [0, 3.48, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16975 | 雨滴传感器 | sm_l5_yudichuanganqi.prefab | Box [0.27, 0.38, 0.06] | [0, 0.2, -0.01] (轴心在底部) | 静态×1 | - | [1.66, 1.55, 1.55] | 0 | - |
| 16976 | 蒸汽收银机 | sm_l5_zhengqishouyinji.prefab | Box [2.38, 1.38, 1.99] | [-0.27, -0.02, 0.99] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 16980 | 卡皮巴拉大炮发射炮弹 | kapibaladapao.prefab | Box [1, 1, 1] (+1个) | [0, 0.45, 0.1] (轴心在底部) | 静态×1 | sunhuaicefan, idle(1.60s,循环), fashepaodan | [1, 1, 1] | 2 | - |
| 16981 | 时日环 | shirihuan.prefab | Box [1.81, 1.4, 2] | [0, 0.65, 0] (轴心在底部) | - | anim(2.00s,循环) | [1, 1, 1] | 0 | - |
| 16982 | 一串小魅惑蘑菇弹 | sm_l4_mohuanmogu_01.prefab | Box [1, 1, 3.98] | [0, 0.41, -1.45] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 16983 | 一串中魅惑蘑菇弹 | sm_l4_mohuanmogu_02.prefab | Box [1.31, 1.24, 4.7] | [0, 0.42, -1.38] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 16984 | 一串大魅惑蘑菇弹 | sm_l4_mohuanmogu_03.prefab | Box [1.54, 1.52, 6.02] | [0, 0.43, -1.46] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 16985 | 一串超大魅惑蘑菇弹 | sm_l4_mohuanmogu_04.prefab | Box [2.04, 1.84, 7.68] | [0, 0.45, -1.38] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 16986 | 毒水池 | sm_l4_gsgc_shuichi_01.prefab | Box [10.31, 2.07, 23.73] | [0, 1.04, 0] (轴心在底部) | 静态×1 | - | [1, 0.52, 1] | 0 | - |
| 16987 | 游动浮光鲤 | fuguangli.prefab | Box [0.25, 0.25, 0.85] | [0, 0.14, 0] (轴心在底部) | - | youdong(0.80s,循环), idle(2.00s,循环) | [1, 1, 1] | 0 | - |
| 17001 | 大日晷 | sm_l5_darigui.prefab | Box [9.42, 0.62, 8.96] Trigger | [-0.03, 0.31, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17002 | 小日晷 | sm_l5_xiaorigui.prefab | Box [7.47, 0.38, 7.47] Trigger | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17003 | 古代瓦罐 | sm_l5_gudaiwaguan.prefab | Box [0.77, 0.66, 0.72] Trigger | [0, 0, 0.36] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17004 | 火晶 | sm_l5_huojing.prefab | Box [0.71, 0.72, 0.51] Trigger | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17005 | 将军令牌 | sm_l5_jiangjunlingpai.prefab | Box [0.16, 0.22, 0.07] Trigger | [0.01, 0.16, -0.01] (轴心偏下) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17006 | 锦囊道具 | sm_l5_jinnangdaoju.prefab | Box [0.19, 0.19, 0.19] | [-0, 0.17, 0] (轴心偏下) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17007 | 木咋特鸟蛋1 | sm_l5_daoju_dan_01.prefab | Box [0.38, 0.47, 0.38] | [0, 0.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17008 | 木咋特鸟蛋2 | sm_l5_daoju_dan_02.prefab | Box [0.38, 0.47, 0.38] Trigger | [0, 0.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17009 | 打开待机武器箱 | sm_l5_xiangzi_01.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | dakai_idle(1.00s,循环), bihe_idle(1.00s,循环), dakai, bihe | [1, 1, 1] | 0 | - |
| 17010 | 峡谷关大门 | sm_l5_xiagu_damen.prefab | Box [8.03, 9.36, 2.17] (+3个) | [0, 4.68, 0.27] (轴心在底部) | 静态×4 | - | [1, 1, 1] | 4 | - |
| 17014 | 进化芯片大 | sm_l4_jinhuaxinpian_03.prefab | Box [0.74, 0.54, 0.18] Trigger | [0, 0.27, 0.06] (轴心在底部) | 静态×2 | - | [2.46, 2.46, 2.46] | 2 | - |
| 17016 | 蒸汽无人机 | zhengqiwurenji.prefab | Box [1.25, 0.65, 0.65] | [0, 0.3, 0] (轴心在底部) | - | walk(2.00s,循环), idle(2.00s,循环), run(2.00s,循环), zhengqiwurenji_anim(2.00s,循环) | [1, 1, 1] | 1 | - |
| 17075 | 雨伞架 3把 | sm_l5_yusanjia_01.prefab | Box [0.69, 0.95, 0.69] | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17255 | 空挂点_y | empty_y.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | MeshPartSettings |
| 17260 | 泥便便 | sm_l5_bianbian.prefab | Box [0.24, 0.24, 0.21] | [0, 0, 0.11] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17261 | 黄牛泥塑像 | sm_l5_huangniudiaoxiang.prefab | Box [1.35, 0.97, 1.83] | [-0.04, -0.14, 0.91] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17262 | 金子堆 | sm_l5_xiaoyubi.prefab | Box [1.85, 1.17, 2.08] | [-0.54, 0.46, -0.08] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 17263 | 星座壁画 虎 | sm_l4_xingzuobihua_hu.prefab | Box [7.72, 6.96, 3.16] Trigger | [0, 3.48, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17264 | 星座壁画 鹊 | sm_l4_xingzuobihua_que.prefab | Box [7.72, 6.96, 3.16] Trigger | [0, 3.48, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17268 | 飞鸽传书 | sm_l6_feigechuanshu_02.prefab | Box [0.2, 0.23, 0.71] | [-0.01, 0.11, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17269 | 飞鸽传书02 | sm_l6_feigechuanshu_01.prefab | Box [0.83, 0.1, 0.56] | [0, 0.05, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17274 | 发光时空之眼 | shikongzhiyan.prefab | Box [2.15, 2.4, 1] | [0, 1.1, 0] (轴心在底部) | - | idle(2.00s,循环) | [1, 1, 1] | 0 | - |
| 17280 | 五色宝石 粉宝石 | sm_l6_baoshi_fen.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17281 | 五色宝石 黄宝石 | sm_l6_baoshi_huang.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17282 | 五色宝石 蓝宝石 | sm_l6_baoshi_lan.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17283 | 五色宝石 绿宝石 | sm_l6_baoshi_lv.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17284 | 五色宝石 紫宝石 | sm_l6_baoshi_zi.prefab | Box [0.22, 0.33, 0.12] | [-0.01, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17285 | 橙子兵法 | sm_l6_chengzibinfa.prefab | Box [0.35, 0.04, 0.56] | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [100, 100, 100] | 0 | - |
| 17292 | 被打断消失飞箭 | sm_l5_feijian_daduan.prefab | Box [0.32, 0.05, 0.55] Trigger | [-0.08, 0, 0.32] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17293 | 被打断消失箭雨 | sm_l5_jianyu_daduan.prefab | Box [0.78, 0.13, 0.94] Trigger | [-0.07, 0.01, 0.51] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17391 | 飞箭 | sm_l5_feijian.prefab | Box [0.28, 0.05, 0.51] Trigger | [-0.06, 0, 0.51] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17392 | 箭雨 | sm_l5_jianyu.prefab | Box [0.66, 0.15, 0.88] Trigger | [-0.06, 0.01, 0.48] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17393 | 一堆黄金香蕉 | sm_l5_yiduihuangjinxiangjiao.prefab | Box [0.52, 0.35, 0.22] Trigger | [0.07, 0.03, 0.12] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17394 | 一根黄金香蕉 | sm_l5_yigenhuangjinxiangjiao.prefab | Box [0.29, 0.08, 0.17] Trigger | [0, 0, 0.1] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17395 | 锦囊 | sm_L5_jinnang.prefab | Box [0.31, 0.39, 0.35] Trigger | [0, 0.22, 0.05] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17398 | 牢笼 | sm_l2_laolong.prefab | Box [3.25, 2.73, 3.64] Trigger | [0.01, 1.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17560 | 雨伞架 2把 | sm_l5_yusanjia.prefab | Box [0.69, 0.95, 0.69] | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17564 | 燃烧的火晶 | sm_l5_huojing02.prefab | Box [0.71, 0.72, 0.51] Trigger | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17567 | 喵朝军营帐篷完整 | sm_l5_hdzk_jianzhu_02.prefab | Box [11.89, 7.6, 13.73] Trigger | [0, 3.8, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17568 | 待机时空之眼 | sm_l5_shikongzhiyan.prefab | Box [2.14, 0.76, 2.12] Trigger | [0, 0, 1.11] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17569 | 损坏侧翻卡皮巴拉大炮 | sm_l5_kapibaladapao_2.prefab | Box [0.9, 0.55, 1.25] Trigger | [-0.11, 0.28, 0.15] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17570 | 待机卡皮巴拉大炮 | sm_l5_kapibaladapao_1.prefab | Box [0.9, 0.55, 1.25] | [-0.11, 0.28, 0.15] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17571 | 卡皮巴拉军营帐篷 | sm_l5_kapibala.prefab | Box [11.89, 7.6, 13.73] Trigger | [0, 3.8, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17572 | 被轰炸卡皮巴拉军营帐篷 | sm_l5_kapibala_po.prefab | Box [11.88, 6.51, 13.54] | [0, 3.25, -0.1] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17573 | 发光大日晷 | sm_l5_darigui02.prefab | Box [9.42, 0.62, 8.96] Trigger | [-0.03, 0.31, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17574 | 发光小日晷 | sm_l5_xiaorigui02.prefab | Box [7.47, 0.38, 7.47] Trigger | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17576 | 胡萝卜 | sm_l5_hulubo.prefab | Box [0.46, 0.89, 0.43] Trigger | [0, 0.45, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17577 | 待机大蒸汽战舰 | sm_l5_kpbl_zhanchuan_01.prefab | Box [17.55, 6, 8.53] Trigger (+1个) | [-0.57, 2.56, -0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 17578 | 小蒸汽战舰 | sm_l5_weicheng_xiaochuan.prefab | Box [13.53, 3.66, 6.87] Trigger (+1个) | [-0.67, 1.81, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 17579 | 待机浮光鲤 | sm_l5_fuguangli.prefab | Box [0.1, 0.4, 0.13] Trigger | [0, 0.01, 0.06] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17758 | 时空之石 | sm_L5_shikongzhishi.prefab | Box [0.68, 0.68, 0.12] | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17955 | 关闭待机武器箱 | sm_l5_xiangzi_02.prefab | Box [1.32, 0.85, 0.83] Trigger (+1个) | [0, 0.41, 0.31] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 17956 | 持续出现电流武器箱 | sm_l5_xiangzi_03.prefab | Box [1.32, 0.57, 1.05] Trigger (+1个) | [0, 0.3, 0.05] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 17957 | 睡莲 | sm_l6_jinglingshuilian.prefab | Box [0.79, 0.44, 0.76] | [-0.03, 0.19, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 17958 | 痒痒蒲公英 | sm_l6_yangyangpugongying.prefab | Box [0.34, 0.45, 0.31] | [-0.01, 0.15, -0.01] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17959 | 晕晕向日葵 | sm_l6_yunyunxiangrikui.prefab | Box [0.37, 0.42, 0.17] | [0, 0.17, 0.05] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17960 | 寒冰蓝玫瑰 | sm_l6_hanbinglanmeigui.prefab | Box [0.27, 0.37, 0.24] | [-0.01, 0.17, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17961 | BMI计算器 | sm_L6_BMIjisuanqi.prefab | Box [0.66, 0.44, 0.04] | [-0, 0.22, -0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17962 | 普通打印机 | sm_L6_putondayinji.prefab | Box [1.35, 0.93, 0.81] | [0, 0.24, -0.15] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17963 | 奢侈品打印机 | sm_L6_shechipindayinji.prefab | Box [1.35, 0.91, 0.88] | [0, 0.22, -0.14] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17964 | 自动播种机 | sm_L6_zidongbozhongji.prefab | Box [1.19, 0.68, 1.19] | [0, 0.31, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17965 | 嘟嘟车 | duduche.prefab | Box [4.32, 7, 16.78] | [0, 3.47, 0] (轴心在底部) | - | idle(2.00s,循环), move(1.33s,循环) | [1, 1, 1] | 1 | - |
| 17966 | 粉花粉弹 | sm_l6_huafendan_02.prefab | Box [2.09, 1.6, 2.22] | [0, 0.15, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 17967 | 蓝花粉弹 | sm_l6_huafendan_01.prefab | Box [2.09, 1.6, 2.22] | [0, 0.15, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 17968 | 绿花粉弹 | sm_l6_huafendan_04.prefab | Box [2.09, 1.6, 2.22] | [0, 0.15, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 17969 | 黄花粉弹 | sm_l6_huafendan_03.prefab | Box [2.09, 1.6, 2.22] | [0, 0.15, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 17981 | 监狱门 | jianyumen.prefab | Box [18, 19, 15] | [0, 8.5, 0] (轴心在底部) | - | kaimen(2.33s,一次), idle | [1, 1, 1] | 1 | - |
| 17983 | 好大的芝麻 | sm_l6_zhima_01.prefab | Box [1.48, 0.56, 1.37] | [0, 0.25, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17984 | 心想事橙（大） | sm_l6_chengzi_01.prefab | Box [1.34, 0.46, 1.17] | [0.01, 0.23, -0] (轴心在底部) | 静态×1 | - | [1.2, 1.2, 1.2] | 0 | - |
| 17985 | 心想事橙（小） | sm_l6_chengzi_02.prefab | Box [1.19, 0.77, 1.13] | [-0.03, 0.38, 0] (轴心在底部) | 静态×1 | - | [0.9, 0.9, 0.9] | 0 | - |
| 17987 | 打开的峡谷关大门 | sm_l5_xiagu_damen_02.prefab | Box [11.86, 11.1, 12.54] (+3个) | [-0.35, 14.7, -0.22] (轴心偏下) | 静态×4 | - | [1, 1, 1] | 4 | - |
| 17988 | 皇族套装 | sm_l6_huangzutaozhuang.prefab | Box [2.1, 1.89, 1.09] | [0, 0.91, 0] (轴心在底部) | 静态×6 | - | [1, 1, 1] | 6 | - |
| 17989 | 小乌云 | sm_l6_wuyun.prefab | Box [10.14, 5.72, 4.67] | [-0.46, 2.86, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 17990 | 检测狗 | jiancegou.prefab | Box [0.67, 1.16, 1.16] (+1个) | [0, 0.5, 0.07] (轴心在底部) | 静态×1 | idle(1.60s,循环), saomiao, run(0.53s,循环), walk(1.07s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 17991 | 佛系解毒丹 | sm_l6_jieduwan.prefab | Box [0.06, 0.06, 0.05] Trigger | [0, 0.03, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 17992 | 金蛋1 | sm_l6_dan_01.prefab | Box [1.99, 0.27, 1.75] Trigger (+1个) | [0.01, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 2 | - |
| 17993 | 金蛋2 | sm_l6_dan_02.prefab | Box [1, 1, 1] Trigger (+2个) | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 2 | - |
| 17994 | 金蛋3 | sm_l6_dan_03.prefab | Box [0.62, 0.77, 0.22] Trigger (+1个) | [0, 0.77, 0.5] (轴心偏下) | - | - | [1, 1, 1] | 2 | - |
| 17995 | 金蛋4 | sm_l6_dan_04.prefab | Box [1.24, 1.53, 1.24] Trigger (+2个) | [0, 0.74, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 3 | - |
| 17996 | 金蛋5 | sm_l6_dan_05.prefab | Box [1.24, 1.53, 1.24] Trigger (+1个) | [0, 0.74, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 17997 | 金蛋6 | sm_l6_dan_06.prefab | Box [1.24, 1.53, 1.24] Trigger (+1个) | [0, 0.74, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 17998 | 金蛋7 | sm_l6_dan_07.prefab | Box [1.99, 0.27, 1.75] Trigger (+1个) | [0.01, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 2 | - |
| 17999 | 金蛋8 | sm_l6_dan_08.prefab | Box [1.24, 1.53, 1.24] Trigger (+1个) | [0, 0.74, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 18000 | 金蛋9 | sm_l6_dan_09.prefab | Box [1.24, 1.53, 1.24] Trigger (+1个) | [0, 0.74, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 18001 | 空白金蛋 | sm_l6_dan_10.prefab | Box [1.09, 1.51, 1.09] Trigger (+1个) | [0.06, 0.72, -0.04] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 18002 | 砸开金蛋1 | sm_l6_dan_posun_01.prefab | Box [2.52, 1.19, 1.64] Trigger (+1个) | [0.64, 0.59, 0.12] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 18003 | 砸开金蛋2 | sm_l6_dan_posun_02.prefab | Box [2.52, 1.19, 1.64] Trigger (+1个) | [0.64, 0.59, 0.12] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 18004 | 砸开金蛋3 | sm_l6_dan_posun_03.prefab | Box [2.52, 1.19, 1.64] Trigger (+1个) | [0.64, 0.59, 0.12] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 18005 | 砸开金蛋4 | sm_l6_dan_posun_04.prefab | Box [1.99, 0.27, 1.75] Trigger (+2个) | [0.01, 0, -0.07] (轴心居中) | - | - | [1, 1, 1] | 3 | - |
| 18006 | 砸开金蛋5 | sm_l6_dan_posun_05.prefab | Box [1.99, 0.27, 1.75] Trigger (+1个) | [0.01, 0, -0.07] (轴心居中) | - | - | [1, 1, 1] | 2 | - |
| 18007 | 砸开金蛋6 | sm_l6_dan_posun_06.prefab | Box [1.99, 0.27, 1.75] Trigger (+1个) | [0.01, 0, -0.07] (轴心居中) | - | - | [1, 1, 1] | 2 | - |
| 18008 | 砸开金蛋8 | sm_l6_dan_posun_08.prefab | Box [1.99, 0.27, 1.75] (+1个) | [0.01, 0, -0.07] (轴心居中) | - | - | [1, 1, 1] | 2 | - |
| 18009 | 砸开金蛋空白 | sm_l6_dan_posun_10.prefab | Box [1.99, 0.27, 1.75] Trigger (+1个) | [0.01, 0, -0.03] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 18010 | 砸金蛋锤 | sm_l6_zadanchuizi.prefab | Box [0.33, 0.49, 0.26] Trigger (+1个) | [0, 0.25, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 18011 | 金鸡兽宝箱 | sm_l6_baoxiang.prefab | Box [0.9, 1.03, 0.74] Trigger (+1个) | [0, 0.52, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 18012 | 豪宅券 | sm_l6_juan_02.prefab | Box [1.22, 1.53, 0.27] Trigger | [0, 0.76, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18013 | 免费御膳券 | sm_l6_juan_01.prefab | Box [1.22, 1.53, 0.27] Trigger | [0, 0.76, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18014 | 天穹仪 | tianqiongyi_01.prefab | Box [1.3, 1.27, 1.33] | [0, 0.81, 0.25] (轴心在底部) | 蒙皮×1 | shaomiao(1.60s,循环), zuoyouhuangdong(1.60s,循环), idle(1.60s,循环) | [1, 1, 1] | 6 | - |
| 18016 | 新版天穹仪 | tianqiongyi_03.prefab | Box [1.3, 1.27, 1.33] | [0, 0.78, 0.27] (轴心在底部) | 蒙皮×1 | shaomiao(1.60s,循环), zuoyouhuangdong(1.60s,循环), idle(1.60s,循环) | [1, 1, 1] | 6 | - |
| 18017 | 盖世英雄金锅锅 | sm_l6_tianqiongyi_04.prefab | Box [0.99, 0.38, 0.86] Trigger | [0, 0.18, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18018 | 白菜仙人掌激光 | sm_l6_baicaixianrenzhangjiguang.prefab | Box [0.39, 0.42, 0.3] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18019 | 蘑菇土豆天使炮 | sm_l6_mogutudoutianshipao.prefab | Box [0.39, 0.45, 0.38] Trigger | [0.02, 0.22, -0.06] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18020 | 投射土豆炮弹的蘑菇土豆天使炮 | mogutudoutianshipao.prefab | Capsule r=0.2,h=0.7 (+1个) | [0, 0.35, 0] | - | attack, idle(1.60s,循环) | [1, 1, 1] | 1 | - |
| 18021 | 菠萝西瓜脉冲弹 | sm_l6_boluoxiguamaichongdan.prefab | Box [0.29, 0.42, 0.24] | [0, 0.22, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18022 | 发射脉冲弹菠萝西瓜脉冲弹 | boluoxiguamaichongdan.prefab | Capsule r=0.2,h=0.7 (+1个) | [0, 0.35, 0] | - | idle(1.60s,循环), attack | [1, 1, 1] | 2 | - |
| 18128 | 蜡烛 | sm_kejianbuji_lazhu.prefab | Box [0.18, 0.38, 0.16] | [-0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18129 | 宝箱 | sm_kejianbuji_baoxiang.prefab | Box [1.08, 0.86, 0.83] | [0, 0.43, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18130 | 九婴碎片 | sm_l1_jiuyinsuipian.prefab | Box [0.58, 0.83, 0.55] | [0, 0.41, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18131 | 《刺客机关屋观光手册》 | sm_l2_cikeguanguangshouce.prefab | Box [0.35, 0.04, 0.56] | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18132 | 门上的锁 | sm_l2_menshangdesuo.prefab | Box [0.83, 0.67, 0.08] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18133 | 龙王茶壶 | sm_l2_longwangchahu.prefab | Box [0.89, 0.73, 0.58] | [0, 0.36, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18327 | 鲁班锁 | lubansuo.prefab | Box [0.85, 0.5, 0.55] | [0, 0.22, 0] (轴心在底部) | - | idle(2.00s,循环) | [1, 1, 1] | 0 | - |
| 18358 | 土 | sm_l6_zhiwushitou_01.prefab | Box [0.32, 0.04, 0.29] Trigger | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [2, 2, 2] | 0 | - |
| 18359 | 凹凸曼西瓜 | sm_l6_xigua.prefab | Box [0.19, 0.24, 0.19] Trigger | [0, 0.12, 0] (轴心在底部) | 静态×1 | - | [2, 2, 2] | 0 | - |
| 18360 | 天使蘑菇 | sm_l6_mogu.prefab | Box [0.35, 0.28, 0.26] Trigger | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [2, 2, 2] | 0 | - |
| 18361 | 超级菠萝 | sm_l6_boluo.prefab | Box [0.32, 0.18, 0.31] Trigger (+1个) | [0.01, 0.23, 0.01] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 18362 | 傲娇白菜 | sm_l6_dabaicai_01.prefab | Box [0.49, 0.36, 0.41] Trigger | [-0.02, 0.18, 0] (轴心在底部) | 静态×1 | - | [2, 2, 2] | 0 | - |
| 18363 | 拽酷仙人掌 | sm_l6_xianrenzhang_01.prefab | Box [0.22, 0.08, 0.04] Trigger (+1个) | [0, 0.12, 0.11] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 18525 | 检测结果出现代码 | sm_l6_jiancejieguo.prefab | Box [0.3, 0, 0.4] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18530 | 天穹仪破碎版 | tianqiongyi_posui.prefab | Box [1.3, 1.27, 1.33] | [0, 0.78, 0.27] (轴心在底部) | 蒙皮×1 | shaomiao(1.60s,循环), zuoyouhuangdong(1.60s,循环), idle(1.60s,循环) | [1, 1, 1] | 6 | - |
| 18531 | 嘟嘟车+卡皮巴拉司机 | duduche+siji.prefab | Box [4.35, 5, 12] (+1个) | [0, 2.45, -0.35] (轴心在底部) | 静态×1 | idle(1.33s,循环), move(1.33s,循环) | [1, 1, 1] | 2 | - |
| 18532 | 嘟嘟车+乘客 | duduche+chengke.prefab | Box [4.35, 5, 12] (+1个) | [0, 2.45, -0.35] (轴心在底部) | 静态×1 | idle(1.33s,循环), move(1.33s,循环) | [1, 1, 1] | 2 | - |
| 18646 | 食人花 | shirenhua.prefab | Box [1.75, 3, 1.68] (+1个) | [0, 1.27, 0] (轴心在底部) | 静态×1 | fengkuangyaobai(0.53s,循环), bizuihujiu(1.33s,循环), bizuiidle(1.33s,循环), zhangzuiidle(1.33s,循环), yao(1.00s,一次) | [1, 1, 1] | 2 | - |
| 18647 | 蒸汽破空 | zhengqipokong_jl.prefab | Box [2.72, 5.85, 6.42] (+1个) | [0, 2.88, -1] (轴心在底部) | 静态×1 | hundongtizi, run(0.53s,循环), idle(1.60s,循环), walk(1.07s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 18652 | 坦克 | tanke.prefab | Box [6.29, 8.06, 8.63] (+1个) | [0, 3.83, 0] (轴心在底部) | 静态×1 | yidong(0.67s,循环), kaipao, idle(2.00s,循环) | [1, 1, 1] | 2 | - |
| 18658 | 大乌云 | sm_l6_wuyun_02.prefab | Box [50.66, 15.22, 26.75] Trigger | [-2.31, 7.61, 0.84] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 18659 | 祈雨大炮 | sm_L3_qiyudapao.prefab | Box [1.67, 2, 4.16] | [0, 1, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 19283 | 马车 | sm_dh_mache.prefab | Box [3.4, 2.35, 2.32] Trigger | [-0.42, 1.18, -0.26] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 19352 | 定水神针 | sm_kejianbuji_jingubang.prefab | Box [0.81, 7.98, 0.81] Trigger | [0, 3.99, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 19354 | 黑色大山 | sm_cg_heisedashan.prefab | Box [311.48, 267.62, 271.84] Trigger | [-4.25, 133.66, -1.25] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 19851 | 全向车 | yingjian_quanxiangche.prefab | Box [9.5, 5, 8] (+1个) | [0, 2.25, -1.22] (轴心在底部) | 静态×1 | xiangzuopingyi(2.00s,循环), idle(2.00s,循环), youzhuan(2.00s,循环), run(2.00s,循环), zuozhuan(2.00s,循环) | [1, 1, 1] | 2 | - |
| 19856 | 黄牛外卖 | sm_yj_huangniuwaimai.prefab | Box [0.76, 0.66, 0.5] | [0, 0.31, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 19857 | 牛车（破损版） | sm_cg_mache_01.prefab | Box [2.46, 1.6, 4.4] | [0, 0.72, -0.3] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 19858 | 牛车 | sm_cg_mache_02.prefab | Box [2.24, 1.7, 4.2] | [0, 0.85, -0.32] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20167 | 黑色直线 | sm_zhixianheixian.prefab | Box [1.08, 0, 14.1] Trigger | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20168 | 转弯黑线 | sm_zhuanwanheixian.prefab | Box [9.34, 0, 9.97] Trigger | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20169 | 重点区域 | sm_zhongdianquyu.prefab | Box [9.13, 0, 4.63] Trigger | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20170 | 积雪 | sm_l4_xuekuai_01.prefab | Box [0.67, 0.66, 0.72] Trigger | [0, 0.25, 0] (轴心在底部) | 静态×1 | - | [1, 0.44, 1] | 0 | - |
| 20172 | 大冰块 | sm_yj_dabingkuai.prefab | Box [5.93, 4.2, 5.3] Trigger | [0.35, 2.1, -0.28] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20709 | 全向车_外卖 | yingjian_quanxiangche_hnwm.prefab | Box [0.76, 0.66, 0.5] (+2个) | [0, 0.31, 0] (轴心在底部) | 静态×3 | xiangzuopingyi(2.00s,循环), idle(2.00s,循环), youzhuan(2.00s,循环), run(2.00s,循环), zuozhuan(2.00s,循环) | [1, 1, 1] | 5 | - |
| 20737 | 零星几块木板 | sm_l7_muban_02.prefab | Box [3.61, 0.54, 2.19] | [-0.35, 0.24, -0.2] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20738 | 建材 | sm_l7_muban_01.prefab | Box [2.97, 0.73, 3.14] | [0, 0.29, 0.52] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20739 | 打人柳树枝 | sm_l7_daoju_liuzhi.prefab | Box [1.27, 0.68, 0.43] | [-0.58, 0.32, -0.14] (轴心在底部) | 静态×1 | - | [1.88, 1.88, 1.88] | 0 | - |
| 20740 | 金币 | sm_l7_daoju_jinbi.prefab | Box [0.63, 0.11, 0.63] | [0, 0.05, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20758 | 传奇法袍 | sm_L7_chuanqifapao.prefab | Box [0.87, 1.67, 0.68] Trigger | [0, 0.84, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20761 | 小木牌 | sm_l7_daoju_mupai.prefab | Box [0.32, 0.34, 0.12] | [0.02, 0.17, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20762 | 十八般厨艺箱 | sm_l7_daoju_chuyixiang.prefab | Box [0.39, 0.39, 0.39] | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20763 | 卷子 | sm_l7_daoju_shijuan.prefab | Box [0.34, 0.03, 0.26] | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20767 | 魔药桌 | sm_l7_yingdi_shiyanzhuo.prefab | Box [4.71, 3.82, 2.95] | [-0.29, 1.92, 0.45] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20768 | 保安树种子 | sm_l7_daoju_zhongzi.prefab | Box [0.7, 0.91, 0.81] | [0, 0.46, 0.05] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20771 | 魔法异闻录 | sm_L7_mofayiwenlu.prefab | Box [0.26, 0.34, 0.11] | [0, 0.17, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20774 | 录取通知书 | sm_l7_dj_tongzhishu.prefab | Box [0.18, 0.09, 0] | [0, 0.05, 0] (轴心在底部) | 静态×1 | - | [6.12, 6.12, 6.12] | 0 | - |
| 20775 | 杯子 | sm_l7_daoju_shuibei.prefab | Box [0.5, 0.35, 0.39] | [0, 0.17, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20776 | 打铁台 | sm_l7_daoju_datietai.prefab | Box [0.74, 0.61, 0.64] | [0, 0.3, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20777 | 铜钳锅 | sm_l7_daoju_guo_01.prefab | Box [2.77, 2.13, 2.64] | [0, 1.06, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20781 | 泡泡a | sm_l7_dj_zimu_a.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20782 | 泡泡d | sm_l7_dj_zimu_d.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20783 | 泡泡N | sm_l7_dj_zimu_dan.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20784 | 泡泡h | sm_l7_dj_zimu_h.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20785 | 泡泡i | sm_l7_dj_zimu_i.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20786 | 泡泡n | sm_l7_dj_zimu_n.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20787 | 泡泡s | sm_l7_dj_zimu_s.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20788 | 泡泡U | sm_l7_dj_zimu_u.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20789 | 泡泡W | sm_l7_dj_zimu_w.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20790 | 泡泡Y | sm_l7_dj_zimu_y.prefab | Box [0.57, 0.56, 0.56] | [0, 0.27, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 20797 | 打人柳嘴炮1 | sm_l7_dj_zuipao_01.prefab | Box [0.7, 0.12, 0.06] | [-0.02, 0.05, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20798 | 打人柳嘴炮2 | sm_l7_dj_zuipao_02.prefab | Box [0.7, 0.12, 0.06] | [-0.02, 0.05, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20814 | 回响光谱01 | sm_l7_huixiangguangpu_01.prefab | Box [0.34, 0.34, 0.34] | [0, 0.15, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20815 | 回响光谱02 | sm_l7_huixiangguangpu_02.prefab | Box [0.34, 0.34, 0.34] | [0, 0.15, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20816 | 回响光谱03 | sm_l7_huixiangguangpu_03.prefab | Box [0.34, 0.34, 0.34] | [0, 0.15, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20817 | 回响光谱04 | sm_l7_huixiangguangpu_04.prefab | Box [0.34, 0.34, 0.34] | [0, 0.15, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20818 | 回响光谱05 | sm_l7_huixiangguangpu_05.prefab | Box [0.34, 0.34, 0.34] | [0, 0.15, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20819 | 回响光谱06 | sm_l7_huixiangguangpu_06.prefab | Box [0.34, 0.34, 0.34] | [0, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20821 | 石中杖底石 | sm_l7_shizhongzhangdishi.prefab | Box [1.54, 1.1, 1.4] | [-0.06, 0.55, -0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20822 | 乾坤袋 | sm_l7_daoju_qiankundai.prefab | Box [0.47, 0.39, 0.44] | [0, 0.17, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20823 | 魔镜 | sm_l7_daoju_mojing.prefab | Box [0.94, 1.44, 0.15] | [0, 0.66, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20824 | 魔法马车 | sm_l7_mofamache.prefab | Box [2.62, 1.86, 4.31] Trigger | [0, 0.93, 0.32] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20825 | 关闭魔法宝箱 | sm_l7_mofabaoxiang02.prefab | Box [2.61, 1.36, 1.68] (+2个) | [0, 0.67, 0.69] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20826 | 飞天扫帚 | sm_l7_feitiansaozhou.prefab | Box [0.59, 2.47, 0.56] | [-0.04, 1.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20827 | 飞天扫帚（队长） | sm_l7_feitiansaozhou_duizhang.prefab | Box [0.59, 2.47, 0.56] | [-0.04, 1.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20828 | 飞天扫帚（百灵） | sm_l7_feitiansaozhou_bailing.prefab | Box [0.59, 2.47, 0.56] | [-0.04, 1.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20829 | 飞剑 | sm_L7_feijian.prefab | Box [0.73, 3.28, 0.23] Trigger | [0, 1.64, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20830 | 打开魔法宝箱 | sm_l7_mofabaoxiang.prefab | Box [2.61, 1.36, 1.68] (+2个) | [0, 0.67, 0.69] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20831 | 传奇魔杖 | sm_L7_chuanqimozhang.prefab | Box [0.11, 0.86, 0.09] Trigger | [0, 0.44, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20832 | 果立成果实 | sm_l7_guolicheng.prefab | Box [0.83, 0.87, 0.74] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20834 | 痒痒种子枪 | sm_L7_yangyangzhongziqiang.prefab | Box [0.3, 0.32, 0.24] | [0, 0.14, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20835 | 藏宝图 | sm_l7_daoju_cangbaotu.prefab | Box [0.91, 0, 0.66] | [0, -0, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20837 | 普通法袍 | sm_l7_putongfapao.prefab | Box [0.87, 1.05, 0.42] Trigger | [0, 0.53, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20838 | 美食摊 | sm_l7_dj_meishitan.prefab | Box [4.84, 4.2, 3.69] | [0.11, 2.03, 0.21] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 20841 | 时间之匙（完整） | sm_l7_yaoshi_01.prefab | Box [0.7, 0.2, 0.67] Trigger | [0, 0.04, -0.04] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20842 | 时间之匙碎片01 | sm_l7_yaoshisuipian_01.prefab | Box [0.3, 0.12, 0.3] Trigger | [0, 0.04, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20843 | 时间之匙碎片02 | sm_l7_yaoshisuipian_02.prefab | Box [0.3, 0.12, 0.28] Trigger | [0, 0.04, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20844 | 时间之匙碎片03 | sm_l7_yaoshisuipian_03.prefab | Box [0.24, 0.12, 0.27] Trigger | [0, 0.04, -0.01] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20845 | 时间之匙碎片04 | sm_l7_yaoshisuipian_04.prefab | Box [0.24, 0.12, 0.27] Trigger | [0, 0.04, -0.01] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20846 | 时间之匙碎片05 | sm_l7_yaoshisuipian_05.prefab | Box [0.3, 0.12, 0.28] Trigger | [0, 0.04, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20847 | 时间之匙碎片06 | sm_l7_yaoshisuipian_06.prefab | Box [0.42, 0.21, 0.38] Trigger | [0, 0.04, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20850 | 魔法马车 | mofamache.prefab | Box [4.2, 4, 8.02] | [0, 2, 0] (轴心在底部) | - | idle, yidong(1.17s,循环) | [1, 1, 1] | 0 | - |
| 20851 | 现代汽车01 | sm_l7_Car_01.prefab | Box [4.98, 1.8, 2.52] Trigger | [-0.48, 0.89, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 20852 | 现代汽车02 | sm_l7_Car_02.prefab | Box [4.98, 1.8, 2.52] | [-0.48, 0.89, -0.01] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 20870 | 保安树01 | baoanshu01.prefab | Box [1, 0.95, 1] (+1个) | [0, 0.45, 0.1] (轴心在底部) | 静态×1 | idle(1.33s,循环), attack | [1, 1, 1] | 4 | 其它脚本×2 |
| 20871 | 保安树02 | baoanshu02.prefab | Box [1.2, 1.4, 1.2] (+1个) | [0, 0.65, 0] (轴心在底部) | 静态×1 | attack, yezipaida, idle(1.33s,循环), run(0.73s,循环), walk(1.00s,循环) | [1, 1, 1] | 4 | 其它脚本×2 |
| 20872 | 保安树03 | baoanshu03.prefab | Box [1.45, 2.5, 1.35] (+1个) | [0, 1.2, 0] (轴心在底部) | 静态×1 | attack, idle(1.33s,循环), walk(0.80s,循环) | [1, 1, 1] | 4 | 其它脚本×2 |
| 20873 | 保安树04 | baoanshu04.prefab | Box [1.85, 3.4, 1.95] | [0, 1.65, 0] (轴心在底部) | - | idle(1.33s,循环), attack | [1, 1, 1] | 2 | 其它脚本×2 |
| 20921 | 魔法三色灯 | sm_l7_daoju_sansedeng.prefab | Box [0.75, 1.77, 0.57] | [0, 0.88, 0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20922 | 魔女包浆钳锅 | sm_l7_daoju_guanzi.prefab | Box [3.37, 1.96, 2.5] | [0, 0.98, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20925 | 毒刺 | sm_l7_duci.prefab | Box [4.9, 0.59, 0.96] Trigger | [-0.09, 0, 0.59] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20926 | 锤子 | sm_l7_dj_chuizi.prefab | Box [0.36, 0.66, 0.22] | [0, 0.32, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20927 | 锄头 | sm_l7_dj_chutou.prefab | Box [0.27, 0.85, 0.38] | [0, 0.42, -0.12] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20928 | 天才笔记 | sm_L7_tiancaibiji.prefab | Box [0.29, 0.37, 0.15] | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20929 | 百灵记忆球 | sm_l7_bailingjiyiqiu.prefab | Box [0.22, 0.22, 0.22] | [0, 0, 0.12] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20930 | 炼金器材（桃子用） | sm_L7_lianyaodaoju.prefab | Box [0.08, 0.13, 0.08] | [0, 0.07, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 20931 | 几页笔记 | sm_l7_dj_biji_01.prefab | Box [0.66, 0.1, 0.49] | [0.14, -0.03, 0.09] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 21035 | 魔法三色灯亮红灯 | sm_l7_daoju_sansedeng_hong.prefab | Box [3.19, 2.49, 2.66] Trigger | [-0.27, 1.24, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21036 | 魔法三色灯亮黄灯 | sm_l7_daoju_sansedeng_huang.prefab | Box [0.75, 1.77, 0.57] | [0, 0.88, 0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21037 | 魔法三色灯亮绿灯 | sm_l7_daoju_sansedeng_lv.prefab | Box [0.75, 1.77, 0.57] | [0, 0.88, 0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21038 | 普通魔镜 | sm_l7_daoju_mojing_02.prefab | Box [0.94, 1.44, 0.15] Trigger | [0, 0.66, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21061 | 无人机 | wurenji.prefab | Box [1.65, 0.63, 1] | [-0.07, 0.35, 0] (轴心在底部) | - | talk(3.73s,一次), Run(1.33s,循环), walk(1.33s,循环), diantou, huanxiao, yaotou, run(1.33s,循环), Idle, gongji, yihuo, sousuo, Idle2 | [1, 1, 1] | 2 | - |
| 21064 | 箭头 | jiantou.prefab | Box [0.72, 0.53, 0.2] | [-0.03, 0.31, 0.01] (轴心在底部) | - | Take 001(2.00s,循环) | [1, 1, 1] | 0 | - |
| 21164 | 营地工地01 | sm_l7_yingdi_gongdi_01.prefab | Box [17.3, 5.6, 20.12] | [0.6, 3.59, 0.3] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 21165 | 营地工地02 | sm_l7_yingdi_gongdi_02.prefab | Box [16.8, 5.77, 16.36] | [4.38, 5.78, 2.7] (轴心偏下) | - | - | [1, 1, 1] | 0 | - |
| 21166 | 营地-小木屋 | sm_l7_yingdi_xiaomuwu.prefab | Box [10.42, 11.49, 16.1] | [2.53, 6.68, 1.4] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21167 | 营地-NPC宿舍 | sm_l7_yingdi_sushe.prefab | Box [15.82, 11.36, 15.86] | [-2.3, 6.21, 1.96] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 21259 | 花间露藤蔓 | L7_huajianluyounian.prefab | Box [1.68, 1.49, 0.66] | [0.05, 0.25, 0.24] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21281 | 巨大荷花 | sm_l7_judahehua.prefab | Capsule r=1.4,h=3.1 (+2个) | [0, 1.5, 0] | 静态×1 | heshang_idle(2.00s,循环), heshang, idle(2.00s,循环) | [1, 1, 1] | 3 | - |
| 21286 | 运输路线-运送目的地 | sm_l8_yunsumudidi.prefab | Box [9.7, 0, 7.5] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21287 | 运输路线-货物装车点 | sm_l8_huowuzhuangchedian.prefab | Box [8.04, 0, 14.91] | [0.83, 0, -3.73] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21288 | 运输路线-绿色方块区域 | sm_l8_yunsuluxianfangkuai.prefab | Box [2, 0, 2] Trigger | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21289 | 运输路线-棕色方块区域 | sm_l8_yunsuluxianfangkuai02.prefab | Box [2, 0, 2] Trigger | [0, 0, 0] | 静态×1 | - | [1.56, 1.56, 1.56] | 0 | - |
| 21301 | 自动行驶路线图 | sm_l8_luxiantu.prefab | Box [33.68, 23.7, 0] Trigger | [-0.92, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21302 | 取货送货路线图 | sm_l8_luxiantu02.prefab | Box [33.68, 23.7, 0] Trigger | [-0.92, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21305 | 黑将 | sm_L8_jiang.prefab | Box [1.2, 2.09, 1.28] Trigger | [-0, 1.04, -0.14] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21306 | 黑士 | sm_L8_shi.prefab | Box [1.2, 2.13, 1.1] Trigger (+1个) | [0.03, 1.06, 0.03] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21307 | 黑卒 | sm_L8_bing.prefab | Box [1.1, 1.79, 1.48] | [-0, 0.9, 0.22] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21308 | 黑车 | sm_L8_che.prefab | Box [1.11, 1.48, 1.38] Trigger | [-0, 0.74, -0] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21309 | 红炮 | sm_L8_pao02.prefab | Box [1.1, 1.26, 1.71] Trigger | [-0, 0.63, 0.04] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21310 | 红车 | sm_L8_che02.prefab | Box [1.11, 1.48, 1.38] Trigger | [-0, 0.74, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21311 | 红兵 | sm_L8_bing02.prefab | Box [1.1, 1.79, 1.48] | [-0, 0.9, 0.22] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21312 | 红帅 | sm_L8_jiang02.prefab | Box [1.2, 2.09, 1.28] Trigger | [-0, 1.04, -0.14] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21313 | 马撕客旗子 | sm_l8_dj_mskqz.prefab | Box [1.8, 3.18, 0.96] Trigger | [0, 1.59, 0] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21314 | 激励马人横幅 | sm_l8_dj_hengfu.prefab | Box [17.6, 4.23, 0.88] Trigger | [0, 2.11, 0] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21315 | 红仕 | sm_L8_shi02.prefab | Box [1.2, 2.13, 1.1] Trigger (+1个) | [0.03, 1.06, 0.03] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21316 | 黑砲 | sm_L8_pao.prefab | Box [1.1, 1.26, 1.71] Trigger | [-0, 0.63, 0.04] (轴心在底部) | 静态×1 | - | [2.2, 2.2, 2.2] | 0 | - |
| 21317 | 装魔药的坩埚 | sm_l8_daoju_myqg.prefab | Box [3.43, 1.6, 2.97] Trigger | [0, 0.8, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21318 | 花瓣账单 | sm_l8_daoju_huaban.prefab | Box [1.21, 1.3, 0.16] Trigger | [0, 0.65, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21319 | 喇叭 | sm_L8_laba.prefab | Box [0.31, 0.45, 0.61] | [0, 0.23, 0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21320 | 不一定唤龙笛 | sm_l8_longdi.prefab | Box [1.02, 0.83, 0.72] Trigger | [-0, 0.38, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21323 | 保安树苗 | sm_l7_baoanshumiao.prefab | Box [0.48, 0.48, 0.29] | [0, 0, 0.14] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21324 | 一张画 | sm_L8_yizhanghua.prefab | Box [0.28, 0.29, 0] | [-0, 0.15, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21343 | 松果 | songguo.prefab | Box [0.3, 0.3, 0.3] | [0, 0.15, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 21387 | 魔法隔离屋 | sm_l8_geliwu_01.prefab | Box [16.04, 10.9, 11.77] | [0, 5.21, 0] (轴心在底部) | 静态×4 | - | [1, 1, 1] | 4 | - |
| 21388 | 打字机 | sm_l9_dj_daziji.prefab | Box [0.81, 0.65, 0.66] Trigger | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21389 | 借阅记录 | sm_l9_dj_jyjl.prefab | Box [0.62, 0.42, 0.12] Trigger | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21390 | 神笔-笔杆（半成品）漂浮发光 | sm_l9_dj_shengbi_02.prefab | Box [0.4, 0.5, 0.4] (+1个) | [-0.06, 1.37, 0] (轴心偏下) | - | idle(2.00s,循环), huahua | [1, 1, 1] | 1 | - |
| 21391 | 神笔-笔杆+毛（完整）漂浮发光 | sm_l9_dj_shengbi_01.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 1 | - |
| 21392 | 神笔造墨锦囊 | sm_l9_dj_zmjn.prefab | Box [0.76, 0.61, 0.47] Trigger | [0, 0.3, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21393 | 隐形兽尾毛 | sm_l9_dj_weimao.prefab | Box [0.17, 0.3, 0.01] Trigger | [-0.07, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21394 | 纸团 | sm_l9_dj_zhituan.prefab | Box [0.45, 0.39, 0.44] Trigger | [0, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21395 | 空的脑机接口 | sm_l8_daoju_pbj.prefab | Box [5.63, 8.26, 6.09] | [0.91, 4.01, 0] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 21397 | 神器合集 | shenqiheji.prefab | Box [0.8, 0.4, 0.5] | [0, 1.29, 0] (轴心偏下) | - | dakai(1.00s,一次), dakai_idle(1.33s,循环), idle(1.33s,循环) | [1, 1, 1] | 0 | - |
| 21399 | 龙蛋 | sm_L8_longdan.prefab | Box [0.4, 0.53, 0.4] | [0, 0.27, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21402 | 黑马人脑机接口 | heimarenpaobuji.prefab | Box [5.2, 7.5, 4.5] | [0, 3.9, 0] (轴心在底部) | - | run(0.53s,循环), idle(1.60s,循环) | [1, 1, 1] | 1 | 其它脚本×1 |
| 21403 | 红马人脑机接口 | hongmarenpaobuji.prefab | Box [5.2, 7.5, 4.5] | [0, 3.9, 0] (轴心在底部) | - | run(0.53s,循环), idle(1.60s,循环) | [1, 1, 1] | 1 | 其它脚本×1 |
| 21404 | 棕马人脑机接口 | zongheimarenpaobuji.prefab | Box [5.2, 7.5, 4.5] | [0, 3.9, 0] (轴心在底部) | - | run(0.53s,循环), idle(1.60s,循环) | [1, 1, 1] | 1 | 其它脚本×1 |
| 21406 | 智能小车+厨艺箱 | zhinengxiaoche.prefab | Box [1.92, 1.2, 3.5] (+1个) | [0, 0.55, 0.5] (轴心在底部) | 静态×1 | idle(2.00s,循环), youzhuan_guajian(1.07s,循环), xianghou_guajian(1.07s,循环), xiangqian_guajian(1.07s,循环), xianghou(1.07s,循环), chuxian, idle_guajian(1.00s,循环), zuozhuan(1.07s,循环), xiangqian(1.07s,循环), youzhuan(1.07s,循环) | [1, 1, 1] | 2 | - |
| 21407 | 智能小车+魔法坩埚 | zhinengxiaoche_mofaganguo.prefab | Box [1.92, 1.2, 3.5] (+1个) | [0, 0.55, 0.5] (轴心在底部) | 静态×1 | idle(2.00s,循环), youzhuan_guajian(1.07s,循环), xianghou_guajian(1.07s,循环), xiangqian_guajian(1.07s,循环), xianghou(1.07s,循环), chuxian, idle_guajian(1.00s,循环), zuozhuan(1.07s,循环), xiangqian(1.07s,循环), youzhuan(1.07s,循环) | [1, 1, 1] | 2 | - |
| 21548 | 路线 | sm_l8_luxian.prefab | Box [32.79, 0, 14.92] Trigger | [-13.19, 0, 5.84] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21574 | 龙宝宝3D精灵 | longbaobao_jingling.prefab | Box [1, 1.45, 1] (+1个) | [0, 0.75, 0] (轴心在底部) | 静态×1 | shizhefei, chengcheng, liulei, shifangshandian, duozaishenhoutantou, tiaoqilaidapenti, fuhua, run(0.67s,循环), baidonggebo, idle(1.33s,循环), walk(0.93s,循环), luchuduzi | [1, 1, 1] | 4 | 其它脚本×1 |
| 21581 | 魔植白术 | sm_l8_daoju_baishu.prefab | Box [0.99, 1.27, 0.71] Trigger | [0, 0.64, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21582 | 魔植茯苓 | sm_l8_daoju_fuling.prefab | Box [1.28, 1.41, 0.86] Trigger | [0, 0.71, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21583 | 龙蛋02 | sm_L8_longdan_02.prefab | Box [0.4, 0.53, 0.4] | [0, 0.27, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21585 | 字母龙鳞a | sm_L8_zimulonglina.prefab | Box [0.25, 0.3, 0.06] Trigger | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21586 | 字母龙鳞b | sm_L8_zimulonglinb.prefab | Box [0.25, 0.3, 0.06] Trigger | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21587 | 字母龙鳞c | sm_L8_zimulonglinc.prefab | Box [0.25, 0.3, 0.06] | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21588 | 字母龙鳞k | sm_L8_zimulonglink.prefab | Box [0.25, 0.3, 0.06] Trigger | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21589 | 字母龙鳞m | sm_L8_zimulonglinm.prefab | Box [0.25, 0.3, 0.06] Trigger | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21590 | 字母龙鳞o | sm_L8_zimulonglino.prefab | Box [0.25, 0.3, 0.06] Trigger | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21591 | 字母龙鳞z | sm_L8_zimulonglinz.prefab | Box [0.25, 0.3, 0.06] Trigger | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21595 | 烤糊土层1 | sm_l8_caidi_01.prefab | Box [4.73, 1.03, 4.74] Trigger | [-0.14, 0.52, -0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21596 | 烤糊土层2 | sm_l8_caidi_02.prefab | Box [4.5, 0.76, 4.5] Trigger | [0.03, 0.38, -0.15] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21721 | 景王电脑 | sm_l9_dj_jwdn.prefab | Box [4.25, 2.67, 2.24] | [0, 1.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21722 | 相框01 | sm_l8_mwnj_xk_01.prefab | Box [1.43, 1.09, 0.16] | [0, 0.52, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21723 | 相框02 | sm_l8_mwnj_xk_02.prefab | Box [1.91, 2.47, 0.28] | [0, 1.19, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21724 | 相框03 | sm_l8_mwnj_xk_03.prefab | Box [1.58, 1.45, 0.48] | [0, 0.66, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21725 | 相框04 | sm_l8_mwnj_xk_04.prefab | Box [1.43, 1.77, 0.24] | [0, 0.86, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21726 | 相框05 | sm_l8_mwnj_xk_05.prefab | Box [2.94, 3.86, 0.93] | [0, 1.81, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21727 | 相框06 | sm_l8_mwnj_xk_06.prefab | Box [1.56, 1.51, 0.26] | [0, 0.7, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21728 | 相框07 | sm_l8_mwnj_xk_07.prefab | Box [1.62, 2, 0.33] | [0, 0.98, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21729 | 相框08 | sm_l8_mwnj_xk_08.prefab | Box [1.52, 1.49, 0.44] | [0, 0.67, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21730 | 相框09 | sm_l8_mwnj_xk_09.prefab | Box [1.12, 1.42, 0.43] | [0, 0.62, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21731 | 相框10 | sm_l8_mwnj_xk_10.prefab | Box [1.2, 1.44, 0.23] | [0, 0.67, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21732 | 相框11 | sm_l8_mwnj_xk_11.prefab | Box [1.34, 1.15, 0.21] | [0, 0.48, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21733 | 相框12 | sm_l8_mwnj_xk_12.prefab | Box [1.31, 1.6, 0.33] | [0, 0.68, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21734 | 相框13 | sm_l8_mwnj_xk_13.prefab | Box [1.85, 1.12, 0.33] | [0, 0.51, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21735 | 相框14 | sm_l8_mwnj_xk_14.prefab | Box [1.21, 1.52, 0.31] | [0, 0.68, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21736 | 相框15 | sm_l8_mwnj_xk_15.prefab | Box [1.09, 1.39, 0.36] | [0, 0.61, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21737 | 相框16 | sm_l8_mwnj_xk_16.prefab | Box [1.55, 1.87, 0.27] | [0, 0.9, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21738 | 相框17 | sm_l8_mwnj_xk_17.prefab | Box [1, 1.24, 0.22] | [0, 0.58, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21739 | 相框18 | sm_l8_mwnj_xk_18.prefab | Box [1.67, 1.06, 0.32] | [0, 0.5, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21740 | 相框19 | sm_l8_mwnj_xk_19.prefab | Box [1.5, 1.18, 0.36] | [0, 0.54, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21741 | 相框20 | sm_l8_mwnj_xk_20.prefab | Box [1.42, 1.81, 0.32] | [0, 0.83, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21742 | 相框21 | sm_l8_mwnj_xk_21.prefab | Box [1.31, 1.83, 0.31] | [0, 0.88, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21743 | 相框22 | sm_l8_mwnj_xk_22.prefab | Box [1.03, 1.27, 0.21] | [0, 0.59, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21744 | 相框23 | sm_l8_mwnj_xk_23.prefab | Box [2.38, 1.48, 0.3] | [0, 0.68, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21745 | 相框24 | sm_l8_mwnj_xk_24.prefab | Box [1.39, 1.74, 0.33] | [0, 0.82, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21746 | 相框25 | sm_l8_mwnj_xk_25.prefab | Box [1.34, 1.34, 0.27] | [0, 0.63, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 21749 | 魔法坩埚 | sm_l8_daoju_myqg_02.prefab | Box [3.43, 1.6, 2.97] | [0, 0.8, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 21753 | 智能小车魔药坩埚绿 | zhinengxiaoche_mofaganguo_lv.prefab | Box [1.92, 1.2, 3.5] (+1个) | [0, 0.55, 0.5] (轴心在底部) | 静态×1 | idle(2.00s,循环), youzhuan_guajian(1.07s,循环), xianghou_guajian(1.07s,循环), xiangqian_guajian(1.07s,循环), xianghou(1.07s,循环), chuxian, idle_guajian(1.00s,循环), zuozhuan(1.07s,循环), xiangqian(1.07s,循环), youzhuan(1.07s,循环) | [1, 1, 1] | 2 | - |
| 21998 | 围栏爬藤_精灵版 | weilanpateng_jl.prefab | Box [7.07, 2.83, 1.72] (+1个) | [2.02, 1.34, 0] (轴心在底部) | 静态×1 | idle(1.60s,循环) | [1, 1, 1] | 2 | - |
| 21999 | 6张照片01 | sm_L8_daoju_xiangpian_01.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22000 | 6张照片02 | sm_L8_daoju_xiangpian_02.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22001 | 6张照片03 | sm_L8_daoju_xiangpian_03.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22117 | 6张照片04 | sm_L8_daoju_xiangpian_04.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22118 | 6张照片05 | sm_L8_daoju_xiangpian_05.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22119 | 6张照片06 | sm_L8_daoju_xiangpian_06.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22120 | 装相片的箱子 | sm_l8_daoju_baoxiang.prefab | Box [0.9, 1.03, 0.74] Trigger (+1个) | [0, 0.52, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 22126 | 宝藏堆 | sm_l8_daoju_baozang_01.prefab | Box [6.5, 1.78, 6.84] | [-0.17, 0.66, -1.15] (轴心在底部) | 静态×4 | - | [1, 1, 1] | 4 | - |
| 22127 | 宝藏堆散开 | sm_l8_daoju_baozang_02.prefab | Box [7.39, 1.62, 5.67] | [-0.9, -0.01, -1.06] (轴心居中) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 22131 | 桥板数字2 | sm_l9_banqiao_2.prefab | Box [0.92, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22132 | 桥板数字5 | sm_l9_banqiao_5.prefab | Box [0.92, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22133 | 桥板数字7 | sm_l9_banqiao_7.prefab | Box [0.92, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22134 | 桥板数字9 | sm_l9_banqiao_9.prefab | Box [0.79, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22135 | 桥板英文 i | sm_l9_banqiao_i.prefab | Box [0.92, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22136 | 桥板英文k | sm_l9_banqiao_k.prefab | Box [0.92, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22137 | 桥板英文n | sm_l9_banqiao_n.prefab | Box [0.92, 4.11, 0.19] Trigger | [0, 0, 0.09] (轴心居中) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22138 | 搭桥材料堆 | sm_l9_banqiao.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 22139 | 运输路线-cg | sm_l4_yunsuluxian.prefab | Box [27.91, 0, 41.32] | [8.31, 0, 2.11] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22140 | 营地-学生宿舍01 | sm_l8_xsss_01.prefab | Box [20.1, 3.69, 12.79] (+1个) | [-0.1, 1.69, 0.6] (轴心在底部) | 静态×4 | - | [1, 1, 1] | 4 | - |
| 22141 | 营地-学生宿舍02 | sm_l8_xsss_02.prefab | Box [20.81, 8.61, 14.07] (+1个) | [0.48, 4.05, 2] (轴心在底部) | 静态×5 | - | [1, 1, 1] | 5 | - |
| 22142 | 营地-学生宿舍03 | sm_l8_xsss_03.prefab | Box [21.39, 8.52, 13.02] (+1个) | [-0.1, 4.1, 1.1] (轴心在底部) | 静态×5 | - | [1, 1, 1] | 5 | - |
| 22143 | 营地-学生宿舍04 | sm_l8_xueyuan_fxjz_fangzi_07.prefab | Box [20.38, 12.55, 13.12] (+1个) | [0, 6, 0.6] (轴心在底部) | 静态×4 | - | [1, 1, 1] | 4 | - |
| 22149 | 焦黑痕迹 | sm_l8_daoju_henji_01.prefab | Box [16.33, 1, 10.16] | [2.48, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 22159 | 兽栏-解锁前 | sm_l8_daoju_shigong_01.prefab | Box [11.62, 2.12, 9.81] | [1.09, 0.92, 0.59] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 22160 | 兽栏-解锁后 | sm_l8_daoju_shoulan_01.prefab | Box [16.34, 8.38, 20.08] (+1个) | [-0.99, 5.1, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 22223 | 虚拟屏幕 | sm_L6_xunipingmu.prefab | Box [0.87, 0.59, 0.01] | [0, 0.29, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22224 | 打字机-坏掉 | sm_l9_dj_daziji_po.prefab | Box [1.13, 0.6, 0.87] | [-0.04, 0.27, 0.06] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22225 | 金苹果 | sm_l8_jinpinguo.prefab | Box [0.15, 0.18, 0.15] | [0, 0.09, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22226 | 奇异精灵草 | sm_l8_qiyijinglingcao.prefab | Box [0.56, 0.58, 0.32] | [0.02, 0.29, -0.05] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22227 | 自食奇果 | sm_l8_zishiqiguo.prefab | Box [0.43, 0.33, 0.43] | [0, 0.16, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22228 | 借阅记录 | sm_L9_jieyuejilu.prefab | Box [0.31, 0.21, 0.05] | [0.01, 0.11, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22229 | 《重生之我在喵朝当女帝》 | sm_L9_nvdihua.prefab | Box [3.36, 1.89, 0] | [0, 0.96, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22230 | 欧阳日记本 | sm_L9_ouyangriji.prefab | Box [0.85, 0.38, 0.32] | [-0.12, 0.15, 0.13] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22232 | 打招呼的信鸽 | L9_xinge@skin_dazhaohu.prefab | Box [0.82, 0.49, 0.38] | [-0.07, 0.07, 0.13] (轴心居中) | 蒙皮×1 | fly_luodi, dazhaohu, fly, idle(1.33s,循环) | [1, 1, 1] | 26 | - |
| 22233 | 待机的信鸽 | L9_xinge@skin_daiji.prefab | Box [0.82, 0.49, 0.38] | [-0.07, 0.07, 0.13] (轴心居中) | 蒙皮×1 | feixingluodi, dazhaohu, feixing(0.83s,循环), idle(1.33s,循环) | [1, 1, 1] | 26 | - |
| 22235 | 穿梭秘籍咒-残片01 | sm_l9_chuansuozhou_01.prefab | Box [0.32, 0.4, 0] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22236 | 穿梭秘籍咒-残片02 | sm_l9_chuansuozhou_02.prefab | Box [0.32, 0.39, 0] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22237 | 穿梭秘籍咒-残片完 | sm_l9_chuansuozhou.prefab | Box [0.58, 0.4, 0] | [0, 0.2, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22239 | 祈雨大炮_车轮 | qiyudapao_chelun.prefab | Box [1.5, 3.5, 4.5] (+1个) | [0, 1.65, 0] (轴心在底部) | 静态×1 | idle, run(1.33s,循环) | [1, 1, 1] | 1 | - |
| 22240 | 飞行的信鸽 | L9_xinge@skin_feixing.prefab | Box [0.82, 0.49, 0.38] Trigger | [-0.07, 0.07, 0.13] (轴心居中) | 蒙皮×1 | feixingluodi, dazhaohu, feixing(0.83s,循环), idle(1.33s,循环) | [1, 1, 1] | 26 | - |
| 22241 | 树枝 | sm_cg_shuzhi.prefab | Box [0.72, 0.47, 0.27] | [-0.34, 0.2, -0.08] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22242 | 浮空中转站 | sm_l9_dj_zzz.prefab | Box [3.48, 5.97, 3.48] (+2个) | [0, 5.5, 0] (轴心偏下) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 22245 | 图书馆规则内页 | sm_l9_guizeneiye.prefab | Box [0.33, 0.42, 0] | [-0, 0.21, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22246 | 椅子 | yizi.prefab | Box [1.7, 3.2, 2] (+1个) | [0, 1.5, 0] (轴心在底部) | 静态×1 | idle, run(1.07s,循环) | [1, 1, 1] | 1 | - |
| 22247 | 椅子01 | yizi01.prefab | Box [1.7, 3.2, 2] (+1个) | [0, 1.5, 0] (轴心在底部) | 静态×1 | idle, run(1.07s,循环) | [1, 1, 1] | 1 | - |
| 22248 | 椅子02 | yizi02.prefab | Box [1.7, 3.2, 2] (+1个) | [0, 1.5, 0] (轴心在底部) | 静态×1 | idle, run(1.07s,循环) | [1, 1, 1] | 1 | - |
| 22363 | 马撕客的火箭 | sm_l9_masikehuojian.prefab | Box [6.87, 7.92, 6.15] | [0, 3.98, -0.31] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22364 | 马撕客的火箭坠落 | sm_l9_masikehuojian_zhuiluo.prefab | Box [10, 6.28, 5.94] | [-0.62, 1.89, -0.11] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22366 | 尖叫鸡 | sm_l9_jianjiaoji.prefab | Box [0.4, 0.94, 0.37] | [0, 0.47, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22367 | 空魔药瓶 | sm_l9_dj_moyaoping_01.prefab | Box [0.21, 0.54, 0.21] | [0, 0.27, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22368 | 魔药瓶（装龙泪） | sm_l9_dj_moyaoping_02.prefab | Box [0.21, 0.54, 0.21] | [0, 0.27, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22369 | 会飞的书 | huifeideshu.prefab | Box [1, 0.65, 0.64] (+1个) | [0, 1.1, 0.2] (轴心偏下) | 静态×1 | idle(1.67s,循环), fly, dakai, dakai_loop(1.67s,循环), heshang | [1, 1, 1] | 1 | - |
| 22441 | 浮空魔法U | sm_l9_dj_mofazhuan_u.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22442 | 浮空魔法砖01 | sm_l9_dj_mofazhuan_01.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22443 | 浮空魔法砖02 | sm_l9_dj_mofazhuan_02.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22444 | 浮空魔法砖03 | sm_l9_dj_mofazhuan_03.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22445 | 浮空魔法砖04 | sm_l9_dj_mofazhuan_04.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22446 | 浮空魔法砖C | sm_l9_dj_mofazhuan_c.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22447 | 浮空魔法砖F | sm_l9_dj_mofazhuan_f.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22448 | 浮空魔法砖o | sm_l9_dj_mofazhuan_o.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22449 | 浮空魔法砖T | sm_l9_dj_mofazhuan_t.prefab | Box [0.88, 0.93, 0.88] Trigger | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22576 | 神笔-笔杆+毛（完整）漂浮 | qiankunshenbi_01.prefab | Box [0.7, 1.2, 0.7] | [0, 1.48, 0] (轴心偏下) | - | - | [1, 1, 1] | 1 | - |
| 22577 | 神笔-笔杆（半成品）漂浮 | qiankunshenbi_02.prefab | Box [0.4, 0.5, 0.4] | [-0.06, 1.37, 0] (轴心偏下) | - | idle(2.00s,循环), huahua | [1, 1, 1] | 0 | - |
| 22579 | 被斩断的麻绳 | sm_l9_dj_masheng.prefab | Box [2.11, 0.12, 1.19] | [-0, 0.06, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22581 | 冰箭 | sm_l9_bingjian_01.prefab | Box [0.11, 0.38, 0.1] Trigger | [-0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22582 | 锻造材料堆金子 | sm_l9_dj_cailiaodui_02.prefab | Box [0.46, 0.54, 0.4] Trigger | [0, 0.27, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22583 | 锻造材料堆木头 | sm_l9_dj_cailiaodui_01.prefab | Box [0.42, 0.41, 1.3] Trigger | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22584 | 锻造材料堆石头 | sm_l9_dj_cailiaodui_04.prefab | Box [0.49, 0.48, 0.32] Trigger | [-0.03, 0.24, -0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22585 | 锻造材料堆铁矿 | sm_l9_dj_cailiaodui_03.prefab | Box [0.48, 0.66, 0.27] Trigger | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22586 | 环湖马拉松奖杯 | sm_l9_jiangbei.prefab | Box [0.51, 0.88, 0.32] Trigger | [0, 0.44, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22587 | 金色墨水 | sm_l9_jinsemoshui.prefab | Box [0.27, 0.43, 0.27] Trigger | [0, 0.2, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22588 | 玉砚 | sm_l9_dj_yuyan.prefab | Box [0.72, 0.07, 1.09] | [0, 0.03, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22589 | 玉墨 | sm_l9_dj_yumo.prefab | Box [0.38, 0.55, 0.25] Trigger | [0, 0.28, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22590 | 漂浮 浮动的状态闪现花 | sm_L9_shanxianhua@skin.prefab | Box [0.47, 0.86, 0.42] | [0, 0.83, 0] (轴心偏下) | 蒙皮×1 | shanbazhang, penhuafen, idle(1.67s,循环) | [1, 1, 1] | 9 | - |
| 22591 | 营地升级-增加武器库 | sm_l9_yingdi_duanzao_01.prefab | Box [12.44, 22.93, 11.32] (+1个) | [0.19, 11.46, 0.31] (轴心在底部) | 蒙皮×2 | Take 001(4.00s,循环) | [0.96, 0.96, 0.96] | 12 | - |
| 22592 | 信号弹红  烟花 | sm_l9_dj_xinhaodan_02.prefab | Box [0.19, 1.1, 0.19] | [0, 0.55, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 22593 | 信号弹蓝 | sm_l9_dj_xinhaodan_01.prefab | Box [0.19, 1.1, 0.19] | [0, 0.55, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22594 | 乾坤神笔待机 | sm_l9_dj_shengbi_01b.prefab | Box [0.18, 0.65, 0.06] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22595 | 大炮 | sm_L9_qiyudapao_chelun.prefab | Box [1.67, 1.99, 4.16] Trigger | [0, 1.01, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22601 | 待机2攻城车 | gongchenghuoche.prefab | Box [4.7, 4.7, 27] | [0, 2.35, -4.5] (轴心在底部) | - | run_wuwuqi(2.00s,循环), gongji, idle(2.00s,循环), idle_wuwuqi(2.00s,循环), run(2.00s,循环) | [1, 1, 1] | 0 | - |
| 22602 | 神笔造墨锦囊 | shenbizaomojinnang.prefab | Box [0.75, 0.7, 0.6] | [0, 1.5, 0] (轴心偏下) | - | idle(2.00s,循环), dakai | [1, 1, 1] | 0 | - |
| 22612 | 冰花射击 | sm_l9_binghua_sj.prefab | Box [1.29, 1.37, 1] | [0, 0.66, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 22613 | 冰花碎裂 | sm_l9_binghua_sl.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 22614 | 攻城车毁损 | gongchenghuochesunhuaiban.prefab | Box [4.7, 4.7, 27] | [0, 2.35, -4.5] (轴心在底部) | - | run_wuwuqi(2.00s,循环), gongji, idle(2.00s,循环), idle_wuwuqi(2.00s,循环), run(2.00s,循环) | [1, 1, 1] | 0 | - |
| 22615 | 马人住所 | sm_l9_marenzhusuo_zhusuo.prefab | Box [17.08, 10.87, 15.86] | [0.87, 4.9, -1.5] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 22616 | 隐形兽住所 | sm_l9_yxszs.prefab | Box [4.56, 2.63, 3.89] | [0.22, 1.24, -0.33] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22617 | 发光神笔造墨锦囊 | sm_l9_dj_zmjn02.prefab | Box [0.76, 0.61, 0.47] Trigger | [0, 0.3, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22618 | 强化玉砚 | sm_l9_dj_yuyan02.prefab | Box [0.72, 0.07, 1.09] | [0, 0.03, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22623 | 行使1攻城车 | sm_L9_gongchenghuoche_rw.prefab | Box [1, 1, 1] (+1个) | [0, 0, 0] (轴心居中) | - | run_wuwuqi(2.00s,循环), gongji, idle(2.00s,循环), idle_wuwuqi(2.00s,循环), run(2.00s,循环) | [1, 1, 1] | 29 | - |
| 22624 | 攻击攻城车 | sm_L9_gongchenghuoche_gj.prefab | Box [5.55, 25.78, 5.61] | [0, 5.35, 2.81] (轴心偏移) | - | run_wuwuqi(2.00s,循环), gongji, idle(2.00s,循环), idle_wuwuqi(2.00s,循环), run(2.00s,循环) | [1, 1, 1] | 29 | - |
| 22625 | 行驶2攻城车 | sm_L9_gongchenghuoche_run.prefab | Box [5.55, 25.78, 5.61] | [0, 5.35, 2.81] (轴心偏移) | - | run_wuwuqi(2.00s,循环), gongji, idle(2.00s,循环), idle_wuwuqi(2.00s,循环), run(2.00s,循环) | [1, 1, 1] | 29 | - |
| 22626 | 待机1攻城车 | sm_L9_gongchenghuoche_dw.prefab | Box [5.55, 25.78, 5.61] | [0, 5.35, 2.81] (轴心偏移) | - | run_wuwuqi(2.00s,循环), gongji, idle(2.00s,循环), idle_wuwuqi(2.00s,循环), run(2.00s,循环) | [1, 1, 1] | 29 | - |
| 22749 | 枯萎月光藤-幼苗 | sm_L9_yueguangteng_youmiaokuwei.prefab | Box [0.12, 0.15, 0.07] Trigger | [-0, 0.08, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22750 | 精灵画布 | sm_l9_dj_jlhb.prefab | Box [13.94, 12.17, 1.08] | [-0, 6.11, 0.37] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22751 | 2张高光照片01 | sm_L9_daoju_ggzp_01.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22752 | 2张高光照片02 | sm_L9_daoju_ggzp_02.prefab | Box [1.67, 1.06, 1] (+1个) | [0, 0.49, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22753 | 不会动的画1 | sm_l9_xiangkuang_01c.prefab | Box [1.07, 1.36, 0.03] (+1个) | [0, 0.84, -0.01] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22754 | 不会动的画2 | sm_l9_xiangkuang_01b.prefab | Box [1.27, 1.69, 0.14] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22755 | 不会动的画3 | sm_l9_xiangkuang_01a.prefab | Box [1.07, 1.36, 0.03] (+1个) | [0, 0.84, -0.01] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22756 | 画中人1待机 | sm_l9_hua_01.prefab | Box [1.07, 1.36, 0.03] (+1个) | [0, 0.84, -0.01] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22757 | 画中人1说话 | sm_l9_hua_02.prefab | Box [1.27, 1.69, 0.14] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22758 | 画中人2wink | sm_l9_hua_04.prefab | Box [1.27, 1.69, 0.14] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22759 | 画中人2待机 | sm_l9_hua_05.prefab | Box [1.27, 1.69, 0.14] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22760 | 画中人2说话 | sm_l9_hua_03.prefab | Box [1.27, 1.69, 0.14] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22761 | 月光藤-成熟（结果） | sm_L9_yueguangteng_chengshu.prefab | Box [0.66, 0.71, 0.3] Trigger | [-0.06, 0.35, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22762 | 月光藤果实 | sm_L9_yueguangteng_guoshi.prefab | Box [0.12, 0.13, 0.04] Trigger | [0.01, 0.07, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22763 | 正常月光藤-幼苗 | sm_L9_yueguangteng_youmiao.prefab | Box [0.09, 0.14, 0.06] Trigger | [-0, 0.07, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22765 | 监牢大门打开过程 | sm_l9_jianlaodamen_a.prefab | Box [2.2, 2.55, 2] | [0, 1, 0] (轴心在底部) | - | guanbi_loop(0.03s,一次), dakai_loop(0.03s,一次), dakai(1.30s,一次) | [1, 1, 1] | 0 | - |
| 22766 | 密码锁开锁 | sm_l9_mimasuo02.prefab | Box [1.16, 0.85, 0.32] | [0, 0.43, 0.07] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 22771 | 密码锁待机 | sm_l9_mimasuo01.prefab | Box [1.16, 0.85, 0.32] | [0, 0.43, 0.07] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 22772 | 监牢大门关闭 | sm_l9_jianlaodamen_b.prefab | Box [2.84, 0.7, 0.6] Trigger (+2个) | [0, 0.35, 1.61] (轴心在底部) | 蒙皮×5 | guanbi_loop(0.03s,一次), dakai_loop(0.03s,一次), dakai(1.30s,一次) | [1, 1, 1] | 10 | - |
| 22773 | 监牢大门打开 | sm_l9_jianlaodamen03.prefab | Box [1.86, 1.68, 1.42] (+2个) | [0, 1.84, 1.69] (轴心偏下) | 静态×5 | - | [1, 1, 1] | 6 | - |
| 22774 | 景王电脑蓝屏 | sm_l9_dj_jwdn02.prefab | Box [4.25, 2.67, 2.24] | [0, 1.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 22780 | 高光照片9-1 | sm_l9_gaoguangzhaopian01.prefab | Box [1.59, 0.99, 0.23] (+1个) | [0, 0.5, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22804 | 牛皮纸 | sm_l8_niupizhi.prefab | Box [0.01, 0, 0.01] | [0, 0, 0] (轴心在底部) | 静态×1 | - | [100, 100, 100] | 0 | - |
| 22805 | 高光照片9-2 | sm_l9_gaoguangzhaopian02.prefab | Box [1.59, 0.99, 0.23] (+1个) | [0, 0.5, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 22889 | 《逆袭之龙傲天星途闪耀》 | sm_L9_daoju_ggzp_03.prefab | Box [1.3, 1.96, 0.25] (+1个) | [0, 0.82, 0] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 23261 | 母龙锁链 | sm_l8_mulongsuolian.prefab | Box [2.96, 0.51, 2.48] | [-0.04, 0.43, -0.34] (轴心偏下) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23263 | 《重生之xxxxxxx》01 | sm_l9_dj_xk_01.prefab | Box [1.45, 1.13, 0.16] | [0, 0.51, 0.01] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 23264 | 《重生之xxxxxxx》02 | sm_l9_dj_xk_02.prefab | Box [1.87, 2.41, 0.25] | [0, 1.17, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 23265 | 《重生之xxxxxxx》03 | sm_l9_dj_xk_03.prefab | Box [1.52, 1.39, 0.45] | [0, 0.66, 0.03] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 23266 | 《重生之xxxxxxx》04 | sm_l9_dj_xk_04.prefab | Box [1.38, 1.78, 0.22] | [0, 0.86, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 23414 | 全向车_生命罗卜 | quanxiangche_shengmingluobu.prefab | Box [9.5, 5, 12] (+1个) | [0, 2.25, -0.18] (轴心在底部) | 静态×1 | qianjin, idle3(1.33s,循环), zuozhuan, idle to idle3(1.00s,一次), idle to idle2(2.00s,一次), idle(1.33s,循环), idle2(1.33s,循环), youzhuan, xiangzuopingyi, houtui | [1, 1, 1] | 2 | - |
| 23421 | 美食摊 | sm_yj_canche.prefab | Box [3.56, 3.88, 1.77] | [0.23, 1.54, 0] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 23422 | 玩具摊 | sm_yj_wanjutan.prefab | Box [5.17, 3.54, 3.28] | [0, 1.71, 0] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 23423 | 气球摊 | sm_yj_qiqiutan.prefab | Box [3.59, 4.95, 3.1] | [-0.26, 2.36, -0.35] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 23547 | 保安树叶子 | sm_l9_baoanshuyezi.prefab | Box [0.35, 0.8, 0.25] | [0.02, 0.37, -0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23548 | 一箱胡萝卜 | sm_L9_dj_muxiang_01.prefab | Box [3.57, 1.45, 1.48] | [0, 0.49, 0] (轴心偏移) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 23549 | 热气球条幅 | sm_yj_reqiqiu.prefab | Box [4.74, 15.81, 4.74] | [0, 7.87, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23577 | 小鱼干 | sm_l9_xiaoyugan.prefab | Box [0.36, 0.3, 0.02] | [-0.03, 0.15, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23749 | 小精灵_3D精灵版 | xiaojingling_3Djingling.prefab | Box [1, 1.25, 1] (+1个) | [0, 0.6, 0] (轴心在底部) | 静态×1 | shifa, idle(2.00s,循环), baipose | [1, 1, 1] | 3 | - |
| 23751 | 鹦鹉草叉_3D精灵版 | yingwucaocha_3Djingling.prefab | Box [1.2, 1.9, 1] (+1个) | [0, 0.9, 0.05] (轴心在底部) | 静态×1 | huiwu(1.40s,循环), beijifei(1.60s,循环) | [1, 1, 1] | 3 | - |
| 23753 | 小熊猫马桶撅_3D精灵版 | xiaoxiongmaomatongjue_3Djingling.prefab | Box [1, 2, 1] (+1个) | [0, 1, 0] (轴心在底部) | 静态×1 | beidafei(1.33s,循环), matongjue(1.37s,循环) | [1, 1, 1] | 2 | - |
| 23754 | 冷不丁_3D精灵版 | lengbuding_3Djingling.prefab | Box [1, 2, 1] (+1个) | [0, 1, 0] (轴心在底部) | 静态×1 | songyikouqi, chuxian, daolixingzou(0.80s,循环), yundao_loop(1.33s,循环), daolidaiji(1.60s,循环), gandong, wuyu, zuobengbengyoubengbeng, shengqi, walk(1.07s,循环), zhamao, liukoushui, beidafei(1.60s,循环), chongbai, wuerduo, xiadehoutuizuodishang_loop(1.33s,循环), beishangnanguo, haoqi, kaixin, xiadehoutuizuodishang_start(1.33s,一次), idle(1.60s,循环), fei, haipa, run(0.67s,循环), yundao, jingya, lache_loop(2.33s,循环), taochu, xiadehoutuizuodishang_end(1.20s,一次), chouchu | [1, 1, 1] | 5 | 其它脚本×2 |
| 23794 | 卡皮巴拉士兵06_3D精灵版 | kapibalashibing06_3Djingling.prefab | Box [1, 1.55, 1] (+1个) | [0, 0.75, 0] (轴心在底部) | 静态×1 | idle(2.00s,循环), mobai, beidafei, walk(1.20s,循环), paozao, attack(1.90s,循环) | [1, 1, 1] | 5 | 其它脚本×2 |
| 23795 | 粉红河马_3D精灵版 | fenhonghema_chengnian_3Djingling.prefab | Box [1.63, 2.3, 1.8] (+1个) | [0, 1.1, 0.27] (轴心在底部) | 静态×1 | wendongxi, idle(2.00s,循环), beidafei, run(0.60s,循环), fly(0.67s,循环), walk(0.97s,循环) | [1, 1, 1] | 5 | 其它脚本×2 |
| 23796 | 运输路线4-4 | sm_l8_yunsumudidi_4-4.prefab | Box [9.7, 0, 3.7] | [0, 0, -0.13] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23797 | 土拨鼠长老红_3D精灵版 | tuboshuzhanglao_red_3Djingling.prefab | Box [1.3, 1.95, 1] (+1个) | [0, 0.9, 0] (轴心在底部) | 静态×1 | zuoyi, kanditu, dichuguaizhang, qisheng, naotou, run(0.93s,循环), idle(1.60s,循环), daodi(0.93s,一次), daodi_idle(2.17s,循环), walk(1.13s,循环), dichuguaizhang_idle(1.60s,循环), beidafei(1.60s,循环) | [1, 1, 1] | 3 | - |
| 23798 | 土拨鼠长老绿_3D精灵版 | tuboshuzhanglao_green_3Djingling.prefab | Box [1.3, 1.95, 1] (+1个) | [0, 0.9, 0] (轴心在底部) | 静态×1 | zuoyi, beidafei(1.60s,循环), kanditu, qisheng, naotou, run(0.93s,循环), idle(1.60s,循环), dichuguaizhang_idle(1.60s,循环), dichuguaizhang, daodi(0.93s,一次), daodi_idle(2.17s,循环), walk(1.13s,循环) | [1, 1, 1] | 3 | - |
| 23799 | 土拨鼠长老蓝_3D精灵版 | tuboshuzhanglao_blue_3Djingling.prefab | Box [1.3, 1.95, 1] (+1个) | [0, 0.9, 0] (轴心在底部) | 静态×1 | zuoyi, kanditu, dichuguaizhang, qisheng, dichuguaizhang_idle(1.60s,循环), naotou, run(0.93s,循环), idle(1.60s,循环), daodi(0.93s,一次), daodi_idle(2.17s,循环), walk(1.13s,循环), beidafei(1.60s,循环) | [1, 1, 1] | 5 | 其它脚本×2 |
| 23909 | 火烈鸟棒子（欧阳版） | huolieniao_bangzi.prefab | Box [0.55, 1.55, 0.75] | [0, 1.4, 0] (轴心偏下) | - | huida, idle(1.33s,循环) | [1, 1, 1] | 2 | - |
| 23930 | 玫瑰花 | meiguihua.prefab | Box [1.35, 2.2, 1.25] | [0.05, 1.05, 0.25] (轴心在底部) | - | yaodong, piao_idle(2.00s,循环), tutou | [1, 1, 1] | 0 | - |
| 23931 | 倒计时玫瑰花 | meiguihua_daojishi.prefab | Box [2.9, 3.5, 3] | [0, 1.75, 0] (轴心在底部) | - | diaoluo, kuwei_idle(2.00s,循环), piao_idle(2.00s,循环) | [1, 1, 1] | 0 | - |
| 23933 | 一车爆炸矿石 | sm_l10_ycks.prefab | Box [1.73, 1.73, 1.17] | [0, 0.86, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23934 | 舔狗魔镜 | sm_l10_jingzi.prefab | Box [2.98, 4.93, 0.77] | [0, 2.46, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23935 | 九转还魂丹 | sm_l10_jzhhd.prefab | Box [0.55, 0.22, 0.55] | [0, 0.11, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23936 | 通关文牒 | sm_l10_tgwd.prefab | Box [0.75, 0.17, 0.39] | [0, 0.08, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23937 | 引爆器 | sm_l10_ybq.prefab | Box [0.8, 0.97, 2.66] | [0, 0.45, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23938 | 一车苹果 | sm_l10_ycpg.prefab | Box [1.73, 1.59, 1.15] | [-0.01, 0.8, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23939 | 意识碎片（蓝色） | sm_l10_yssp.prefab | Box [1.78, 2.27, 0.42] | [0, 1.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23940 | 意识碎片（紫色） | sm_l10_yssp_01.prefab | Box [1.78, 2.27, 0.42] | [0, 1.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23941 | 意识碎片（红色） | sm_l10_yssp_02.prefab | Box [1.78, 2.27, 0.42] | [0, 1.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23942 | 种植指南小册子 | sm_l10_zhidaoshu.prefab | Box [0.53, 0.2, 0.7] | [0, 0.1, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23944 | 棒打柠檬药水满杯 | sm_nmys_man.prefab | Box [0.5, 0.7, 0.5] | [0, 0.3, 0] (轴心在底部) | - | anim(1.60s,循环) | [1, 1, 1] | 0 | - |
| 23956 | 碎掉的意识碎片（红色） | sm_l10_yssp_02_sui.prefab | Box [1.78, 2.27, 0.42] | [0, 1.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23957 | 碎掉的意识碎片（紫色） | sm_l10_yssp_01_sui.prefab | Box [1.78, 2.27, 0.42] | [0, 1.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23958 | 碎掉的意识碎片（蓝色） | sm_l10_yssp_sui.prefab | Box [1.78, 2.27, 0.42] | [0, 1.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 23967 | 大礼帽3D精灵版 | dalimao_3Djingling.prefab | Box [1, 1.2, 1] (+1个) | [0, 0.55, 0] (轴心在底部) | 静态×1 | feixing(0.80s,循环), idle(1.33s,循环) | [1, 1, 1] | 2 | - |
| 23970 | 疯帽匠+大礼帽 | fengmaojiang_dalimao.prefab | Box [1.85, 4, 2] | [-0.15, 2, 0.3] (轴心在底部) | - | anim(1.87s,循环) | [1, 1, 1] | 0 | - |
| 23977 | 朋友一生一起走锁 | sm_l10_suo.prefab | Box [1.72, 0.85, 0.23] (+2个) | [0.02, 0.38, 0] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 24137 | 疯帽匠3D精灵版 | fengmaojiang_3Djingling.prefab | Box [1.2, 3.7, 1.25] (+1个) | [0, 1.8, -0.05] (轴心在底部) | 静态×1 | jifei_loop(1.33s,循环), run(0.67s,循环), shenshouyizhi, huiquan, idle(1.60s,循环), walk(1.07s,循环), shuangshouhuiquan, jingxia | [1, 1, 1] | 4 | 其它脚本×1 |
| 24155 | 老毛虫 | laomaochong.prefab | Box [0.7, 1.6, 1.4] | [0, 0.75, -0.2] (轴心在底部) | - | idle_fennu, qiyun_loop(1.53s,循环), walk_fennu, idle(1.60s,循环), run_fennu, touxiao, kuqi, qiyun, gongji_fennu | [1, 1, 1] | 3 | 其它脚本×1 |
| 24166 | 社牛水晶球 | sm_l10_sheniushuijingqiu.prefab | Box [0.26, 0.28, 0.25] | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24167 | 小铲子（道具） | sm_L10_chanzi.prefab | Box [0.22, 0.49, 0.1] | [0, 0.25, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24168 | 小锄头（道具） | sm_L10_chutou.prefab | Box [0.36, 0.39, 0.1] | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24169 | 苹果花 | sm_l10_pingguohua.prefab | Box [0.4, 0.64, 0.33] | [-0, 0.32, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24171 | 银制匕首 | sm_l10_bishou.prefab | Box [0.29, 0.78, 0.08] | [0, 0.39, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24172 | 行李 | sm_l10_xingli.prefab | Box [1.04, 1.36, 1] Trigger | [-0.01, 0.68, -0.1] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24173 | 快问快答卷 | kwkdj.prefab | Box [1, 1.25, 0.5] | [0, 0.55, 0] (轴心在底部) | - | anim(1.60s,循环) | [1, 1, 1] | 0 | - |
| 24174 | 朋友肖像卷 | xxj.prefab | Box [0.9, 1.25, 0.3] | [0, 0.6, 0] (轴心在底部) | - | anim(1.60s,循环) | [1, 1, 1] | 0 | - |
| 24175 | 茧 | jian.prefab | Box [0.75, 0.9, 0.7] | [0, 0.3, 0] (轴心偏移) | - | niudong(2.27s,一次), idle(0.03s,循环) | [1, 1, 1] | 0 | - |
| 24176 | 茧房 | jianfang.prefab | Box [0.85, 0.85, 0.85] | [0, 0.4, 0] (轴心在底部) | - | idle_guanmen, idle_kaimen | [1, 1, 1] | 0 | - |
| 24177 | 变大蛋糕 | sm_l10_bddg.prefab | Box [1.74, 1.19, 1.74] | [0, 0.6, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24178 | 好事坏事全看见魔法屏 | sm_l10_mfp.prefab | Box [4.69, 2.87, 0.33] | [0, 1.43, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24179 | 205胶水（有求必应屋道具已更新） | sm_l10_jiaoshui.prefab | Box [0.33, 0.93, 0.19] | [0, 0.47, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24180 | 205胶水 | sm_l10_jiaoshui_02.prefab | Box [0.32, 0.82, 0.18] | [0.01, 0.39, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24181 | 玫瑰（半变化形态） | sm_l10_meigui_banbianhuaxingtai.prefab | Box [0.39, 0.6, 0.37] | [0.02, 0.3, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24182 | 狼毒草 | sm_l10_langducao.prefab | Box [0.46, 0.63, 0.38] | [0.02, 0.31, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24184 | 茶壶女茶杯男 | chahunv+chabeinan.prefab | Box [0.95, 0.75, 0.65] | [0, 0.32, 0] (轴心在底部) | - | idle(1.00s,循环), daocha | [1, 1, 1] | 0 | - |
| 24185 | 堆成山的卷子 | sm_l10_yiduijuanzi.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 24190 | 蓝色茶壶 | sm_l10_chhcz_chahu04.prefab | Box [0.4, 0.45, 0.3] | [0, 0.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24191 | 粉色茶壶 | sm_l10_chhcz_chahu01.prefab | Box [0.56, 0.74, 0.44] | [0, 0.37, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24192 | 棕色茶壶 | sm_l10_chhcz_chahu03.prefab | Box [0.45, 0.49, 0.31] | [0, 0.25, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24193 | 紫色茶壶 | sm_l10_chhcz_chahu02.prefab | Box [0.43, 0.22, 0.34] | [0, 0.11, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24194 | 黄色咖啡杯 | sm_l10_chhcz_chabei01.prefab | Box [0.33, 0.15, 0.33] | [0, 0.08, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24195 | 绿色咖啡杯 | sm_l10_chhcz_chabei02.prefab | Box [0.33, 0.15, 0.33] | [0, 0.07, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24198 | 黄色咖啡杯带动画 | chabei01.prefab | Box [0.6, 0.35, 0.6] | [0, 0.12, 0] (轴心偏移) | - | bengtiao(1.00s,循环), idle(1.33s,循环) | [1, 1, 1] | 0 | - |
| 24199 | 绿色咖啡杯带动画 | chabei02.prefab | Box [0.6, 0.35, 0.6] | [0, 0.12, 0] (轴心偏移) | - | bengtiao(1.00s,循环), idle(1.33s,循环) | [1, 1, 1] | 0 | - |
| 24207 | 喷洒装置 | sm_l10_pszz.prefab | Box [1.1, 1.09, 3.16] | [0, 0.54, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24208 | 密码备忘录 | sm_l10_bwl.prefab | Box [0.76, 0.07, 0.39] | [-0, 0.03, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24209 | 全向车-喷药 | sm_quangxiangchepengyao.prefab | Box [21.22, 28.45, 11.07] (+2个) | [0, -18.37, 1.73] (轴心偏移) | - | - | [1, 1, 1] | 3 | - |
| 24344 | 蓝色茶壶动画版 | lansechahu.prefab | Box [0.75, 0.9, 0.7] | [0, 0.35, 0] (轴心在底部) | - | bengtiao(0.67s,循环), idle(1.60s,循环) | [1, 1, 1] | 0 | - |
| 24345 | 棕色茶壶动画版 | zongsechahu.prefab | Box [0.75, 0.9, 0.7] | [0, 0.35, 0] (轴心在底部) | - | bengtiao(0.67s,循环), idle(1.60s,循环) | [1, 1, 1] | 0 | - |
| 24346 | 粉丝茶壶动画版 | fensechahu.prefab | Box [1, 1.4, 1] | [0, 0.6, 0] (轴心在底部) | - | bengtiao(0.60s,循环), idle(1.67s,循环) | [1, 1, 1] | 0 | - |
| 24347 | 紫色茶壶动画版 | zisechahu.prefab | Box [0.8, 0.5, 0.65] | [0, 0.2, 0] (轴心在底部) | - | idle(1.67s,循环), bengtiao(0.60s,循环) | [1, 1, 1] | 0 | - |
| 24400 | 百灵扫帚女童 | bailingsaozhounvtong.prefab | Box [1.2, 4.2, 1.2] | [0, 2, -0.1] (轴心在底部) | - | saohui(3.33s,一次), idle(1.60s,循环) | [1, 1, 1] | 0 | - |
| 24649 | 蓝色地毯 | sm_l10_yscb_ditan_lan.prefab | Box [15.08, 0.04, 15.08] | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24681 | 高光照片L10 | sm_l10_gaoguangzhaopian01.prefab | Box [1.35, 1.12, 0.22] (+1个) | [0, 0.52, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 24682 | 星缘占卜帐篷 | sm_l10_xyzbzp.prefab | Box [10.81, 1.66, 7.81] (+6个) | [-0.01, 0.89, -0.77] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 8 | - |
| 24683 | 龙鳞 | sm_L10_longlin.prefab | Box [0.25, 0.3, 0.06] | [0, 0.15, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24684 | 一滩水 | sm_L10_yitanshui.prefab | Box [1.23, 0.01, 0.81] | [-0.04, 0.01, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24685 | 驱狼铃 | sm_l10_qll.prefab | Box [0.85, 1.8, 0.85] Trigger | [0, 0.9, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24687 | 挣扎痕迹 | sm_L10_zhengzhahenji.prefab | Box [0.45, 0.13, 0.31] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 24700 | 陷阱（开） | sm_L10_xianjingkai.prefab | Box [0.89, 0.13, 0.97] | [-0.06, 0.07, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25074 | 奖杯 | sm_l11_jiangbei.prefab | Box [0.51, 0.39, 0.32] | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25080 | 贝壳珍珠 | beikezhenzhu.prefab | Box [2, 1, 1.79] | [0, 0.4, 0] (轴心在底部) | - | idle(2.00s,循环), dakai(3.33s,一次) | [1, 1, 1] | 0 | - |
| 25085 | 钻石 | sm_l11_zuanshi.prefab | Box [0.91, 1.01, 0.38] | [0, 0.5, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25086 | 碳粉 | sm_l11_tanfen.prefab | Box [1.79, 0.78, 1.72] | [0, 0.39, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25087 | 贝壳 | sm_l11_beike.prefab | Box [1.09, 1.08, 1] | [0, 0.54, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25088 | 珍珠 | sm_l11_zhenzhu.prefab | Box [0.38, 0.38, 0.38] | [0, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25089 | 珍珠粉末 | sm_l11_zhenzhufen.prefab | Box [1.79, 0.78, 1.72] | [0, 0.39, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25090 | 破镜重圆 | sm_l11_pjcy.prefab | Box [0.77, 0.19, 0.77] | [0, 0.1, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25091 | 脆脆红蛋 | sm_l11_hongdan.prefab | Box [0.38, 0.41, 0.38] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25092 | 麦穗 | sm_l11_maisui.prefab | Box [0.46, 0.85, 0.35] | [-0.04, 0.42, -0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25093 | 旋转椅 | sm_l11_xzy_zhuanyi.prefab | Box [2.42, 2.51, 2.42] | [0, 1.24, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25095 | 金子 | sm_l11_jinzi.prefab | Box [0.2, 0.25, 0.18] | [0, 0.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25096 | 寻龙分金尺 | sm_l11_fenjinchi.prefab | Box [0.61, 0.38, 0.06] | [-0.1, 0.19, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25097 | 魔法生化肥料 | sm_l11_huafei.prefab | Box [0.24, 0.34, 0.11] | [0, 0.17, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25111 | 森林之声 | sm_l11_slzs.prefab | Box [0.41, 0.54, 0.04] | [0, 0.27, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25276 | 好事坏事全看见魔法屏01 | sm_l10_mfpwenzi_01.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 25277 | 好事坏事全看见魔法屏02 | sm_l10_mfpwenzi_02.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 25278 | 好事坏事全看见魔法屏03 | sm_l10_mfpwenzi_03.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 25283 | 符咒 | sm_l11_fuzhou.prefab | Box [0.21, 0.56, 0.01] | [0, 0.28, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25284 | 咒语残本 | sm_l11_zycb.prefab | Box [0.74, 0.34, 0.62] Trigger | [0.01, 0.15, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25285 | 狼人被绑 | sm_L10_langren_shengzi.prefab | Box [1.29, 1.09, 0.95] | [0, 0.55, -0.08] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25286 | 长生果 小 | sm_l11_csg_01.prefab | Box [0.05, 0.03, 0.03] | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25287 | 长生果 中 | sm_l11_csg_02.prefab | Box [0.08, 0.05, 0.05] | [0, 0.02, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25288 | 长生果 大 | sm_l11_csg_03.prefab | Box [0.12, 0.07, 0.1] | [0, 0.03, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25425 | 灰烬（金子）地上 | sm_l11_huijingjingzi.prefab | Box [2.39, 0, 2.29] (+1个) | [0, 0, 0] | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25426 | 灰烬（金子)空中 | sm_l11_huijingjingzi02.prefab | Box [0.2, 0.25, 0.18] | [0, 0.13, 0] (轴心在底部) | 静态×1 | - | [5.38, 5.38, 5.38] | 0 | - |
| 25442 | 千面神灯 | sm_l11_qmsd.prefab | Box [2.23, 1.41, 1.12] | [0.19, 0.71, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25450 | 好事坏事全看见魔法屏04 | sm_sm_l10_mfpwenzi_04.prefab | Mesh | - | 静态×1 | - | [1, 1, 1] | 1 | - |
| 25463 | 地球仪 | sm_l11_diqiuyi.prefab | Box [1.04, 1.41, 1] Trigger | [-0, 0.7, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25464 | 天平 | sm_l11_tianping.prefab | Box [1.48, 0.96, 0.63] Trigger | [0, 0.49, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25465 | 烛台 | sm_l11_zhutai.prefab | Box [0.38, 1.06, 0.38] | [0, 0.53, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25466 | 魔法书 | sm_l11_mofashu.prefab | Box [0.63, 0.34, 0.85] | [0, 0.12, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25467 | 魔药瓶 | sm_l11_moyaoping.prefab | Box [0.47, 0.68, 0.47] | [0, 0.34, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25479 | 寻龙分金尺 | fenjinchi.prefab | Box [1.2, 0.75, 0.25] | [-0.15, 0.32, 0] (轴心在底部) | - | zhizuo, luanzhuan(2.17s,一次), idle, zhixieqianyou | [1, 1, 1] | 0 | - |
| 25480 | 千面神灯 | qianmianshendeng.prefab | Box [1.55, 1.5, 1.45] | [0, 0.7, 0] (轴心在底部) | - | idle(1.33s,循环), zhendong, houyi | [1, 1, 1] | 0 | - |
| 25522 | 楼梯指示牌 | sm_l9_dj_lupai.prefab | Box [2.42, 2.89, 1.44] | [0, 1.45, 0] (轴心在底部) | 静态×1 / 粒子×1 | - | [1, 1, 1] | 1 | - |
| 25609 | 社牛水晶球_带动画 | sheniushuijingqiu.prefab | Box [0.6, 0.55, 0.5] | [0, 0.25, 0] (轴心在底部) | - | zhuanquan, idle(1.33s,循环), walk(1.33s,循环), feilaifeiqu, outu | [1, 1, 1] | 0 | - |
| 25612 | 灰色桥板材料j | sm_l9_bancai_shi03.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25613 | 灰色桥板材料l | sm_l9_bancai_shi01.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25614 | 灰色桥板材料r | sm_l9_bancai_shi02.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25615 | 灰色桥板材料u | sm_l9_bancai_shi04.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25616 | 蓝色板桥材料a | sm_l9_bancai_bing01.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25617 | 蓝色板桥材料b | sm_l9_bancai_bing02.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25618 | 蓝色板桥材料m | sm_l9_bancai_bing03.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25619 | 蓝色板桥材料n | sm_l9_bancai_bing04.prefab | Box [0.5, 0.11, 1.04] | [0, 0.11, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 25620 | 魔药瓶（红） | sm_l9_pingzi_06.prefab | Box [0.66, 0.9, 0.65] | [0, 0.45, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25621 | 魔药瓶（黄） | sm_l9_pingzi_02.prefab | Box [0.7, 0.71, 0.7] | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25622 | 魔药瓶（绿） | sm_l9_pingzi_03.prefab | Box [0.45, 0.68, 0.45] | [0, 0.34, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25623 | 魔药瓶（深蓝） | sm_l9_pingzi_01.prefab | Box [0.47, 0.68, 0.47] | [0, 0.34, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25625 | 魔药瓶（紫） | sm_l9_pingzi_04.prefab | Box [0.66, 0.9, 0.65] | [0, 0.45, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25626 | 坩锅（黑） | sm_l8_qianguo.prefab | Box [2.77, 2.13, 2.64] | [0, 1.06, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25627 | 水晶碎片 | sm_l11_shuijingsuipian.prefab | Box [0.4, 0.05, 0.15] | [0.01, 0, 0.11] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25628 | 白色花 | sm_hua.prefab | Box [0.51, 0, 0.49] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25842 | 魔法帽 | sm_L11_mofamao.prefab | Box [1.01, 0.52, 1.29] | [0, 0.28, -0.18] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25843 | 精灵果盘 | jinglingguopan.prefab | Box [0.8, 0.5, 0.85] | [0, 1.3, 0] (轴心偏下) | - | piao_idle | [1, 1, 1] | 0 | - |
| 25844 | 密室大门 | sm_L11_mishidamen.prefab | Box [0.47, 0.49, 0.14] | [0, 0.25, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25845 | 混沌星核 | sm_L11_hundunxinghe.prefab | Box [0.29, 0.29, 0.26] | [-0.01, 0.15, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25846 | 王者之剑 | sm_l11_wangzhezhijian.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25847 | 王者之剑-剑坯 | sm_l11_wangzhezhijian_jianpei.prefab | Box [0.2, 0.07, 1.16] | [0, 0, 0.61] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25848 | 妖精金属 | sm_L11_yaolingjiashu.prefab | Box [0.13, 0.16, 0.03] | [-0.01, 0.08, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25849 | 水球 | sm_L11_shuiqiu.prefab | Box [0.17, 0.17, 0.17] | [0, 0.09, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 25850 | 水晶圈 | shuijinquan.prefab | Box [0.55, 0.6, 0.35] | [0, 0.2, 0] (轴心偏移) | - | piao_idle(2.00s,循环) | [1, 1, 1] | 0 | - |
| 25852 | 智能小车混沌星核 | zhinengxiaoche_chaoshenbochuanganqi.prefab | Box [1.92, 1.2, 3.5] | [0, 0.55, 0.5] (轴心在底部) | - | idle(2.00s,循环), youzhuan_guajian(1.07s,循环), xianghou_guajian(1.07s,循环), xiangqian_guajian(1.07s,循环), xianghou(1.07s,循环), chuxian, idle_guajian(1.00s,循环), zuozhuan(1.07s,循环), xiangqian(1.07s,循环), youzhuan(1.07s,循环) | [1, 1, 1] | 0 | - |
| 25853 | 招财猫 | zhaocaimao.prefab | Box [1, 1, 0.75] | [0, 0.48, -0.05] (轴心在底部) | - | idle(1.73s,循环) | [1, 1, 1] | 0 | - |
| 25891 | 水晶方块 | shuijingfangkuai.prefab | Box [0.66, 0.66, 0.66] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26219 | 舔狗魔镜破碎 | sm_l10_jingziposui.prefab | Box [2.98, 4.93, 0.77] | [0, 2.46, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26290 | 魔药瓶（银） | sm_l9_pingzi_05.prefab | Box [0.7, 0.71, 0.7] | [0, 0.35, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26291 | 服装店（营地11-3） | sm_l1_dj_chuchuangfang.prefab | Box [7.54, 9.23, 8.19] | [0, 4.35, 1.23] (轴心在底部) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 26292 | 水晶 | kuangdong_shuijing01.prefab | Box [0.53, 0.6, 0.31] | [0, 0.3, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26567 | 希斯发3D精灵 | xisifa_3Djingling.prefab | Box [1, 2.75, 1] (+1个) | [0, 1.32, -0.1] (轴心在底部) | 静态×1 | xiangzhi, fangyu_loop(1.20s,循环), tiaoxin, shifa, kongzhong_loop(2.00s,循环), fangyu(0.63s,一次), taishoushifa, walk(1.20s,循环), kongzhong_start(1.90s,一次), daxiao, tongkubaotou, fennu, idle(1.60s,循环), kongzhong_end(0.90s,一次), run(0.67s,循环), yundaozaidi(1.87s,循环), fukong idle(1.60s,循环) | [1, 1, 1] | 5 | 其它脚本×1 |
| 26607 | 王者之剑  蓝 | sm_l11_wangzhezhijian_lan.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26608 | 王者之剑 紫 | sm_l11_wangzhezhijian_zi.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26610 | 一份小抄 | sm_l12_xiaochao.prefab | Box [0.34, 0.43, 0.01] (+1个) | [0, 0.22, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 26686 | 强化符文01 | sm_l12_qhfw.prefab | Box [0.61, 0.75, 0.22] | [0, 0.37, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26687 | 强化符文02 | sm_l12_qhfw02.prefab | Box [0.61, 0.75, 0.22] | [0, 0.37, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26688 | 强化符文03 | sm_l12_qhfw03.prefab | Box [0.61, 0.75, 0.22] | [0, 0.37, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26689 | 强化符文04 | sm_l12_qhfw04.prefab | Box [0.61, 0.75, 0.22] | [0, 0.37, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26692 | 特斯拉时空跑车崭新版 | tesilapaoche_zhanxinban.prefab | Box [5, 4, 12] (+1个) | [0, 2, 0] (轴心在底部) | 静态×1 | idle(1.00s,循环), run(2.00s,循环) | [1, 1, 1] | 1 | - |
| 26693 | 特斯拉时空跑车灰尘版 | tesilapaoche_huichenban.prefab | Box [5, 4, 12] (+1个) | [0, 2, 0] (轴心在底部) | 静态×1 | idle(1.00s,循环), run(2.00s,循环) | [1, 1, 1] | 1 | - |
| 26734 | 一堆岩石 | sm_l12_shitou_01.prefab | Box [7.23, 6.26, 11.31] | [1.38, 2.86, 0.35] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 26736 | 马撕客的操作台 | sm_dj_l8_jinlin_kzt.prefab | Box [7.24, 2.36, 3.7] | [0, 1.12, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 26738 | 碎石障碍 | sm_l11_suishizhangai.prefab | Box [9.38, 1.89, 6.82] | [1.57, 0.92, -0.72] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 26753 | 魔法线圈 | sm_L12_mofaxianquan.prefab | Box [0.91, 0.38, 0.6] | [-0.17, 0.18, -0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26754 | 魔法乙醇汽油 | sm_L12_mofayichunqiyou.prefab | Box [0.42, 0.56, 0.21] | [0, 0.28, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26755 | 特斯拉电塔 | sm_L12_tesiladianta.prefab | Box [3.09, 6.8, 6.45] | [0, 3.37, 0.95] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26756 | 魔法钥匙待机 | sm_l12_yaoshi.prefab | Box [0.28, 0.13, 0.47] | [0, 0.06, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26757 | 法阵的星星01 | sm_l12_szxx_01.prefab | Box [1.09, 1.03, 0.24] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26758 | 法阵的星星02 | sm_l12_szxx_02.prefab | Box [1.09, 1.03, 0.24] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26759 | 法阵的星星03 | sm_l12_szxx_03.prefab | Box [1.09, 1.03, 0.24] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26760 | 法阵的星星04 | sm_l12_szxx_11.prefab | Box [1.09, 1.03, 0.24] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26761 | 法阵的星星05 | sm_l12_fzxx_01.prefab | Box [0.68, 0.58, 0] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26762 | 法阵的星星06 | sm_l12_fzxx_02.prefab | Box [0.72, 0.58, 0] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26763 | 法阵的星星07 | sm_l12_fzxx_03.prefab | Box [0.68, 0.58, 0] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26764 | 法阵的星星08 | sm_l12_fzxx_04.prefab | Box [0.71, 0.58, 0] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26765 | 法阵的星星09 | sm_l12_fzxx_05.prefab | Box [0.68, 0.54, 0] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26766 | 法阵的星星10 | sm_l12_fzxx_06.prefab | Box [0.72, 0.54, 0] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26768 | 魔法钥匙发光 | sm_l12_yaoshi02.prefab | Box [0.28, 0.13, 0.47] | [0, 0.06, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26881 | 应有尽有还可以冥想盆 | sm_l12_mingxiangpen.prefab | Box [0.38, 0.42, 0.43] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26891 | 建材包裹 | sm_l7_jiancaibaoguo.prefab | Box [0.3, 0.3, 0.3] | [0, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26892 | 魔植包裹 | sm_l7_mozhibaoguo.prefab | Box [0.3, 0.3, 0.3] | [0, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 26898 | 降维魔法弹 | sm_l12_jwmfd.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 26917 | 降维魔法剑01 | sm_l12_jiangweimofajian_01.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 26918 | 希斯发未黑化3D精灵版 | xisifa_weiheihua_3djingling.prefab | Box [1, 2.75, 1] (+1个) | [0, 1.32, -0.1] (轴心在底部) | 静态×1 | baoquan, shengqi, run(0.67s,循环), zhanbai(1.87s,循环), gaoxing, ganga, taishou, walk(1.07s,循环), idle(1.60s,循环), xuankong | [1, 1, 1] | 4 | 其它脚本×1 |
| 27068 | 机械臂全向车 | jixiebiquanxiangche.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | - | run(1.33s,循环), idle(1.33s,循环), run_taichazi(1.33s,循环), idle_taichazi(1.33s,循环), taichazi | [1, 1, 1] | 0 | - |
| 27069 | 降维魔法剑02 | sm_l12_jiangweimofajian_02.prefab | Box [1, 2.68, 1] | [-0.3, 0.93, 0] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 27083 | 特斯拉时空跑车发光 | tesilapaoche_faguang.prefab | Box [5, 4, 12] (+1个) | [0, 2, 0] (轴心在底部) | 静态×1 | idle(1.00s,循环), run(2.00s,循环) | [1, 1, 1] | 1 | - |
| 27239 | 机械臂全向车 | jixiebiquanxiangche_jixiebi.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | - | houtui(1.33s,循环), run(1.33s,循环), shenjiazhuadaiji(1.33s,循环), idle(1.33s,循环), shenjiazhua(1.33s,一次), shenjiazhua02(1.33s,一次), shenjiazhua02_idle(1.33s,循环), Azhaoshou | [1, 1, 1] | 0 | - |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | jixiebiquanxiangche_jixiebi_jianzhubaoguo.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | 蒙皮×5 / 静态×1 | idle_jiaqi(1.33s,循环), fangkai, fangxia(3.00s,一次), run_qubijiaqi(1.33s,循环), jiaxiangzi(1.67s,一次), idle_jiaxiangzi(1.33s,循环), jiaqi(3.00s,一次), run_jiaqi(1.33s,循环), run_qubijiaqi02(1.33s,循环) | [1, 1, 1] | 21 | - |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | jixiebiquanxiangche_jixiebi_mozhibaoguo.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | 蒙皮×5 / 静态×1 | idle_jiaqi(1.33s,循环), fangkai, fangxia(3.00s,一次), run_qubijiaqi(1.33s,循环), jiaxiangzi(1.67s,一次), idle_jiaxiangzi(1.33s,循环), jiaqi(3.00s,一次), run_jiaqi(1.33s,循环), run_qubijiaqi02(1.33s,循环) | [1, 1, 1] | 21 | - |
| 27243 | 王者之剑终极 | sm_l11_wangzhezhijian_zhongji.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27247 | 王者之剑寒冰特效 | sm_l11_wangzhezhijian_lan02.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27249 | 王者之剑火焰特效 | sm_l11_wangzhezhijian02.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27250 | 王者之剑空间魔法 | sm_l11_wangzhezhijian_zi02.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27251 | 王者之剑终极特效 | sm_l11_wangzhezhijian_zhongji02.prefab | Box [0.35, 1.13, 0.11] | [0, 0.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27381 | 降维魔法弹（原地） | ef_jiangweimofadanyuandi_01.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 27392 | 曼德拉草3D精灵 | mandelacao_3Djingling.prefab | Box [1, 1.65, 1] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×1 | jianjiao, dishang_idle(1.33s,循环), dixia_idle(1.33s,循环) | [1, 1, 1] | 5 | 其它脚本×2 |
| 27393 | 矮人3D精灵 | airen_3Djingling.prefab | Box [1, 2.5, 1] (+1个) | [0, 1.2, 0] (轴心在底部) | 静态×1 | lunchui, dianzan, idle(1.60s,循环), qili, walk(1.47s,循环), run(1.00s,循环), diantou, taodongxi, zuozhewan(5.13s,循环), duanzao | [1, 1, 1] | 4 | 其它脚本×1 |
| 27394 | 魔法加特林 | sm_L9_ouyang_wuqi1.prefab | Box [1.19, 0.58, 0.36] Trigger | [0, 0.3, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27414 | 傀儡小兵残骸 | sm_L12_kuileixiaobingcanhai.prefab | Box [1.86, 0.88, 2.14] | [-0.16, 0.31, -0.07] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27416 | 王者之剑带动作 | wangzhezhijian_daidongzuo.prefab | Box [1, 1.59, 1] | [0, 1.52, 0] (轴心偏下) | - | attack | [1, 1, 1] | 0 | - |
| 27489 | 王者之剑火焰特效版带动作 | wangzhezhijian_daidongzuo_huoyantexiao.prefab | Box [1, 1.59, 1] | [0, 1.52, 0] (轴心偏下) | - | attack | [1, 1, 1] | 0 | - |
| 27534 | 机械臂全向车装满草 | jixiebiquanxiangche_jixiebi_zhuangmancao.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | - | houtui(1.33s,循环), run(1.33s,循环), shenjiazhuadaiji(1.33s,循环), idle(1.33s,循环), shenjiazhua(1.33s,一次), shenjiazhua02(1.33s,一次), shenjiazhua02_idle(1.33s,循环), Azhaoshou | [1, 1, 1] | 0 | - |
| 27535 | 机械臂全向车夹草 | jixiebiquanxiangche_jixiebi_jiacao.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | - | idle | [1, 1, 1] | 0 | - |
| 27536 | 机械臂全向车夹坩埚 | jixiebiquanxiangche_jixiebi_zhuangmancao_jiaganguo.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | - | idle | [1, 1, 1] | 0 | - |
| 27547 | 魔药速递 龙痘疮 | sm_l8-03-02_wujian_01.prefab | Box [20.3, 0, 20.19] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27548 | 魔药速递 炼魔药 | sm_l8-03-02_wujian_02.prefab | Box [56.29, 2, 40.63] | [-0.6, 0, 0] (轴心居中) | 静态×3 | - | [1, 1, 1] | 3 | - |
| 27549 | 机械臂全向车装货框版 | jixiebiquanxiangche_jixiebi_zhuanghuokuang.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | - | houtui(1.33s,循环), run(1.33s,循环), shenjiazhuadaiji(1.33s,循环), idle(1.33s,循环), shenjiazhua(1.33s,一次), shenjiazhua02(1.33s,一次), shenjiazhua02_idle(1.33s,循环), Azhaoshou | [1, 1, 1] | 0 | - |
| 27551 | 队长魔法袍03_3D精灵 | duizhangmofapaoshengji03_3D.prefab | Box [1.98, 3.07, 1] (+1个) | [0.05, 1.27, 0] (轴心在底部) | 静态×1 | beibang(1.60s,循环), shoujian, jingyataitou(1.60s,循环), dianji, najian, exin, jiebang, shenlanyao, guizhuozhanqilai, daoli_idle(1.60s,循环), walk(1.07s,循环), chouqujiyi, shifa, "\u5C0F\u52A8\u753B", xiaodonghua, naotou, jusang, "\u5C0F\u52A8\u753B03", fadou, "\u5C0F\u52A8\u753B02", idle(1.60s,循环), taodongxi, yundao, turanqichuang, huanhu, taishou, guizhuo_idle(1.60s,循环), huijian, daoli_run(0.60s,循环), huidaiji(1.60s,一次), najianju, qitiao_end(1.27s,一次), nalongdi_idle(1.60s,循环), run(0.67s,循环), haoqi, xiaodonghua02, sichuzhangwang, qitiao_loop(1.50s,循环), mofabang_idle(1.60s,循环), qitiao_start(1.10s,一次), sichuzhangwangzou(2.13s,循环), chuilongdi_loop(1.33s,循环), yundao_shuizhao(1.33s,循环), danshoubeng(2.27s,循环), wujianshu, xingfen, chuilongdi(0.73s,一次), nachulongdi(0.73s,一次), najianju_idle(1.60s,循环), xiaodonghua03, huangzhangbihua | [1, 1, 1] | 5 | 其它脚本×2 |
| 27552 | 雪球0_5_3D精灵 | xueqiuL0_5_3D.prefab | Box [1, 1.34, 1] (+1个) | [0, 0.62, 0] (轴心在底部) | 静态×1 | zihao, dazhaohu, diantou, shizhong(2.97s,一次), didongxi, idle(1.60s,循环), xiao, wuer, piaofu(1.33s,循环), xunipingmu, sikao, daku, yaotou, danxin(1.60s,循环), gaoxing, aojiao(2.53s,循环), siing, wuyu, walk(1.20s,循环), shenshouzhi, jvshouloop, run(0.47s,循环) | [1, 1, 1] | 4 | 其它脚本×2 |
| 27553 | 桃子魔法袍_3D精灵 | taozimofapao_3D.prefab | Box [1.97, 2.74, 1] (+1个) | [0.19, 1.29, 0] (轴心在底部) | 静态×1 | xiaodonghua2, xiaodonghua, diantou, nawuqi_idle(1.60s,循环), shifangmofa(2.57s,一次), chayaochaoqianzhi, run(0.67s,循环), idle(1.60s,循环), rouyanjing, woquan, gangga, taofazhang, walk(1.07s,循环), xianqi, dazhaohu, jusang | [1, 1, 1] | 4 | 其它脚本×1 |
| 27554 | 乌拉乎魔法袍_3D精灵 | wulahumofapao_3D.prefab | Box [2.85, 2.8, 1] (+1个) | [0.12, 1.32, 0] (轴心在底部) | 静态×1 | xiaodonghua2, daxiao, mofabang_idle(1.87s,循环), huangzhangpao(0.47s,循环), xiaodonghua, zhuangbi, run(0.73s,循环), beileijizhong, woquan, beileijizhongxuanyun(1.67s,循环), idle(1.87s,循环), jingya, walk(1.07s,循环), haipa | [1, 1, 1] | 5 | 其它脚本×2 |
| 27555 | 禾木魔法袍_3D精灵 | hemumofapao_3D.prefab | Box [1.82, 2.85, 1] (+1个) | [-0.01, 1.35, 0] (轴心在底部) | 静态×1 | ququ, jieshuo, xiaodonghua02, wuyu, ku, walk(1.07s,循环), yundaozaidi(1.37s,循环), woquan, idle(1.37s,循环), tanshou, xiaodonghua, daxiao, fuyao, haipa, qingqiu, run(0.67s,循环) | [1, 1, 1] | 5 | 其它脚本×2 |
| 27559 | 魔药速递 炼魔药取货区 | sm_l8-03-02_wujian_03.prefab | Box [3.66, 0, 10.01] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27693 | 毕业典礼横幅 | sm_l12_hengfu.prefab | Box [4.58, 1.96, 0.8] Trigger | [0, 0.58, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27694 | 毕业证书 | sm_l12_biyezhengshu.prefab | Box [2.26, 1.11, 1.35] | [-0.03, 0.55, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27695 | 气球装饰 | sm_l12_yqjzs_qiqiu01.prefab | Box [1.42, 3.11, 1.54] | [0, 1.57, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27780 | 机械臂 | sm_l7_jixiebi.prefab | Box [0.25, 0.21, 0.44] (+1个) | [-0, 0.2, -0.25] (轴心偏下) | - | - | [1, 1, 1] | 2 | - |
| 27781 | 营地（7-4B形态）种植田 | sm_l7_zhongzhitian_01.prefab | Box [17.8, 3.41, 17.36] | [0, 1.43, 1.69] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 27782 | 营地（7-4B形态）温室 | sm_l7_wenshi_01.prefab | Box [34.6, 14.73, 18.87] | [0, 7.23, 2.83] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 27816 | 0 | sm_0.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27817 | 1 | sm_1.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27818 | 2 | sm_2.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27819 | 3 | sm_3.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27820 | 4 | sm_4.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27821 | 5 | sm_5.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27822 | 6 | sm_6.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27823 | 7 | sm_7.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27824 | 8 | sm_8.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27825 | 9 | sm_9.prefab | Box [0.1, 0.1, 0] Trigger | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 27871 | 凸显框 | tuxiankuang.prefab | Box [10, 0, 10] (+1个) | [0, 0, 0] | 静态×1 | - | [0.1, 0.1, 0.1] | 0 | - |
| 27956 | 智能小车混沌星核无超声传感 | zhinengxiaoche_hundunxinghe_wuchuanganqi.prefab | Box [1.92, 1.2, 3.5] (+1个) | [0, 0.55, 0.5] (轴心在底部) | 蒙皮×1 / 静态×1 | idle(2.00s,循环), youzhuan_guajian(1.07s,循环), xianghou_guajian(1.07s,循环), xiangqian_guajian(1.07s,循环), xianghou(1.07s,循环), chuxian, idle_guajian(1.00s,循环), zuozhuan(1.07s,循环), xiangqian(1.07s,循环), youzhuan(1.07s,循环) | [1, 1, 1] | 14 | - |
| 28016 | 单格冰块 | sm_l13_bingkuai.prefab | Box [2.69, 0.35, 2.77] | [0, 0.18, 0] (轴心在底部) | 静态×1 | - | [0.37, 0.54, 0.36] | 0 | - |
| 28017 | 营地地砖 | sm_l13_dizhuan.prefab | Box [2.61, 0.28, 2.61] | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [0.38, 0.38, 0.38] | 0 | - |
| 28026 | 红线框1-1 | sm_l13_hongxiankuang01.prefab | Box [0.5, 0, 0.5] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28027 | 红线框2-2 | sm_l13_hongxiankuang02.prefab | Box [1, 0, 1] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28028 | 红线框2-3 | sm_l13_hongxiankuang023.prefab | Box [2, 0, 1] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28029 | 绿线框1-1 | sm_l13_lvxiankuang01.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28030 | 绿线框2-3 | sm_l13_lvxiankuang023.prefab | Box [2, 0, 1] | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28035 | 能源探头 | nengyuantantou.prefab | Box [0.75, 0.75, 0.45] | [0.05, 0.35, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | 其它脚本×1 |
| 28055 | 雷达 | sm_l13_leida.prefab | Box [5.55, 10.5, 5.69] Trigger (+1个) | [-0.03, 5.25, 0.25] (轴心在底部) | 静态×1 | leidachuxian(1.17s,一次), leidadaiji(1.00s,一次), idle(0.56s,循环), hongdiandaiji | [1, 1, 1] | 1 | - |
| 28056 | 袋装种子 | sm_l13_dzzz.prefab | Box [0.33, 0.37, 0.23] | [0, 0.19, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28057 | 冰块 | sm_l13_dj_bingkuai.prefab | Box [35.87, 5.73, 21.26] | [0, 2.87, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28058 | 可燃冰原始状态 | sm_l13_keranbing.prefab | Box [0.48, 0.66, 0.27] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28059 | 椰子树 | sm_l13_yezishu.prefab | Box [8.35, 5.85, 8.22] | [-0.6, 2.92, 0.03] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28063 | 机械臂（装备） | sm_l13_jxb.prefab | Box [1, 1, 1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 12 | - |
| 28064 | 星际服 | sm_L13_xingjifu.prefab | Box [0.5, 0.27, 0.46] | [0, 0.14, -0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28065 | 生物编码药剂粉 | sm_L13shengwubianmayaoji02.prefab | Box [0.39, 0.96, 0.28] Trigger (+2个) | [-0.02, 0.48, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 2 | - |
| 28066 | 生物编码药剂绿 | sm_L13shengwubianmayaoji.prefab | Box [0.39, 0.96, 0.28] Trigger (+2个) | [-0.02, 0.48, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 2 | - |
| 28067 | 普通探头待机状态 | sm_L13_nengyuantantou.prefab | Box [0.34, 0.39, 0.2] | [0.03, 0.19, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28068 | 普通探头成功状态 | sm_L13_nengyuantantou02.prefab | Box [0.34, 0.39, 0.2] | [0.03, 0.19, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28069 | 普通探头工作状态 | sm_L13_nengyuantantou03.prefab | Box [0.34, 0.39, 0.2] | [0.03, 0.19, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28070 | 无人机 | L13_wurenji.prefab | Box [1.5, 0.55, 1.25] | [0, 0.17, -0.06] (轴心偏移) | - | walk(1.33s,循环), idle(1.33s,循环), run(1.33s,循环), fiy(1.33s,循环) | [1, 1, 1] | 1 | - |
| 28075 | 盲盒 | sm_l13_manghe.prefab | Box [1, 1.01, 1.03] | [0, 0.53, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28077 | 合格板子 | sm_l13_hegeban.prefab | Box [12, 0.23, 1.46] | [0, -0.11, 0] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28078 | 电磁板 | sm_l13_tynb_01.prefab | Box [3.67, 1.76, 3.49] | [0, 0.88, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28079 | 太阳能板02 | sm_l13_tynb_02.prefab | Box [3.67, 1.76, 3.49] | [0, 0.88, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28080 | 组装材料 零件箱 | sm_l13_dzgjx.prefab | Box [1.47, 0.19, 1.05] Trigger (+1个) | [0, 0.09, 0.52] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 28081 | 组装材料面板堆01 | sm_l13_mianbandui01.prefab | Box [4.38, 0.25, 0.97] (+2个) | [0, 0.12, 0] (轴心在底部) | - | - | [1, 1, 1] | 3 | - |
| 28082 | 组装材料面板堆02 | sm_l13_mianbandui02.prefab | Box [4.16, 0.23, 1.03] (+8个) | [0, 0.11, 0] (轴心在底部) | - | - | [1, 1, 1] | 9 | - |
| 28083 | 组装材料（普通） | sm_l13_zzcl_01.prefab | Box [5.13, 2.09, 6.21] (+9个) | [-0.28, 0.52, 0.39] (轴心偏移) | - | - | [1, 1, 1] | 9 | - |
| 28084 | 组装材料面板堆01b | sm_l13_mianbandui01b.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28085 | 组装材料面板堆02a | sm_l13_mianbandui01a.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28101 | 能源探头待机状态 | sm_L13_putongtantou_01.prefab | Box [0.38, 0.44, 0.24] | [0.04, 0.2, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28102 | 能源探头工作状态 | sm_L13_putongtantou_02.prefab | Box [0.38, 0.44, 0.24] | [0.04, 0.2, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28103 | 能源探头成功状态 | sm_L13_putongtantou_03.prefab | Box [0.38, 0.44, 0.24] | [0.04, 0.2, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28106 | 物资箱带动画 | wuzixiang_daidonghua.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | dakai_idle(1.00s,循环), bihe_idle(1.00s,循环), dakai, bihe | [1, 1, 1] | 1 | - |
| 28107 | 风车 | sm_l6_dj_fengche01.prefab | Box [12, 20, 12] | [0, 9.5, 0] (轴心在底部) | - | Take 001(2.00s,循环) | [1, 1, 1] | 0 | - |
| 28108 | 魔药园风车建筑 | sm_l7_dj_myy_fengche.prefab | Box [10, 25, 10] | [0, 11.5, 0] (轴心在底部) | 蒙皮×1 | Take 001(2.00s,循环) | [1, 1, 1] | 3 | - |
| 28110 | 水泥地砖 | sm_l13_dizhuan02.prefab | Box [2.61, 0.28, 2.61] | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [0.38, 0.38, 0.38] | 1 | - |
| 28111 | 太阳能光合板（成组） | sm_l13_taiyangban.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28133 | 队长小屋 简易太空舱 | sm_l13_dzxw.prefab | Box [9.06, 6.97, 6.14] (+1个) | [-0.43, 3.46, -0.65] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 28134 | 男生住宅 | sm_l13_hmxw.prefab | Box [13.06, 8.48, 14.85] (+1个) | [0, 4.24, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 28135 | 女生住宅 | sm_l13_nsss.prefab | Box [9.59, 8.64, 7.85] | [0, 4.32, 0.06] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28257 | 材料板 | sm_l13_bingkuai02.prefab | Box [2.69, 0.35, 2.77] | [0, 0.18, 0] (轴心在底部) | 静态×1 | - | [0.37, 0.54, 0.36] | 0 | - |
| 28262 | 周期解码器 工作状态 | sm_l13_jiemaqi_02.prefab | Box [2.88, 1.6, 0.61] | [0, -0.01, 0] (轴心居中) | - | - | [1, 1, 1] | 1 | - |
| 28263 | 周期解码器 待机状态 | sm_l13_jiemaqi_03.prefab | Box [2.88, 1.6, 0.61] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 1 | - |
| 28264 | 物资箱带动画02 | wuzixiang_daidonghua02.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | dakai_idle(1.00s,循环), bihe_idle(1.00s,循环), dakai, bihe | [1, 1, 1] | 1 | - |
| 28265 | 布 | sm_l13_bu.prefab | Box [7, 6, 0.01] | [0, 0, -0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28268 | 材料条1 | sm_l13_bingkuai001.prefab | Box [2.69, 0.35, 0.62] | [0, 0.18, 1.08] (轴心在底部) | 静态×1 | - | [0.37, 0.54, 0.36] | 0 | - |
| 28269 | 材料条2 | sm_l13_bingkuai002.prefab | Box [2.69, 0.23, 0.63] | [0, 0.06, 0] (轴心偏移) | 静态×1 | - | [0.37, 0.54, 0.36] | 0 | - |
| 28270 | 材料条3 | sm_l13_bingkuai003.prefab | Box [2.69, 0.23, 0.62] | [0, 0.06, 0] (轴心偏移) | 静态×1 | - | [0.37, 0.54, 0.36] | 0 | - |
| 28271 | 电磁板02 | sm_l13_tynb02.prefab | Box [3.67, 0.2, 3.67] | [0, 0.03, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28273 | 雷达带动画 | leida_anim.prefab | Box [5.6, 11, 5.5] Trigger | [0, 5.2, 0] (轴心在底部) | - | jiance(2.00s,循环), yujing | [1, 1, 1] | 1 | - |
| 28274 | 机械物件02 | m_l13_jixiewujian02.prefab | Box [2, 2.06, 0.46] | [-0.01, 1.03, 0.09] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28360 | 透明太阳能板 | sm_l13_tynb_02b.prefab | Box [1, 0.18, 1.01] | [-0.05, 0.01, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28364 | 物资库大门 | wuzikudamen.prefab | Box [5.5, 5.5, 6.5] | [0, 2.6, 0] (轴心在底部) | - | dakai(2.30s,一次), kai(0.03s,一次), guan(0.03s,一次) | [1, 1, 1] | 1 | - |
| 28633 | 避雷针塔 | sm_l14_blzt.prefab | Box [3.29, 13.79, 3.29] | [0, 6.89, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28634 | 石墨烯避雷针塔 | sm_l14_blzt_hei.prefab | Box [3.63, 14.45, 3.59] | [0, 6.94, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 28638 | 周期解码器 底座 | sm_l13_jiemaqi_01.prefab | Box [4.46, 1.57, 2.45] | [0, 0.7, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 28656 | 能源探测器 | nengyuantishiqi.prefab | Box [0.3, 0.45, 0.35] | [0.1, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 2 | 其它脚本×1 |
| 28658 | 材料板1-1 | sm_l13_bingkuai02_1.prefab | 无 | - | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28659 | 材料条1 1-1 | sm_l13_bingkuai001_1.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28660 | 材料条2 | sm_l13_bingkuai002_1.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28661 | 材料条3 1-1 | sm_l13_bingkuai003_1.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28662 | 单格冰块1-1 | sm_l13_bingkuai_1.prefab | 无 | - | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28663 | 营地地砖1-1 | sm_l13_dizhuan_1.prefab | 无 | - | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28664 | 水泥地砖1-1 | sm_l13_dizhuan02_1.prefab | 无 | - | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28665 | 螺蛳粉锅 | sm_l15_lsfg.prefab | Box [3.43, 1.6, 2.97] | [0, 0.8, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28666 | 墙上涂鸦 | sm_l15_qsty.prefab | Box [8.64, 5.12, 0] | [0, 2.56, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28668 | 等离子发射器 | sm_L13_denglizifasheqi.prefab | Box [0.15, 0.13, 0.2] | [-0.01, 0.07, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28669 | 制造车间 | sm_l13_zhizaochejian.prefab | Box [1.18, 5, 5.75] (+11个) | [7.63, 5.75, 1.13] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 12 | - |
| 28670 | 蓄电池组升级前 | sm_l13_dcz_01.prefab | Box [1, 1, 1] (+2个) | [0, 0, 0] (轴心居中) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28671 | 蓄电池组升级后 | sm_l13_dcz_02.prefab | Box [0.82, 0.72, 0.82] (+2个) | [0, 7.69, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28672 | 蓄电池组电力不足 | sm_l13_dcz_03.prefab | Box [1, 1, 1] (+2个) | [0, 0, 0] (轴心居中) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28673 | 判断指示灯 红色 | sm_l15_pdzsd_04.prefab | Box [0.33, 0.33, 0.1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28674 | 蓄电池组充满电 | sm_l13_dcz_04.prefab | Box [0.82, 0.72, 0.82] (+2个) | [0, 7.69, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 28675 | 判断指示灯 待机 | sm_l15_pdzsd_03.prefab | Box [0.33, 0.33, 0.1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28676 | 判断指示灯 黄色 | sm_l15_pdzsd_02.prefab | Box [0.33, 0.33, 0.1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28677 | 判断指示灯 绿色 | sm_l15_pdzsd_01.prefab | Box [0.33, 0.33, 0.1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28679 | 矿洞大门 | sm_l15_kg_men.prefab | Box [4.46, 3.53, 2.34] | [0, 1.64, 0] (轴心在底部) | - | kai(0.03s,一次), kaimen(3.33s,一次), guan(0.03s,一次) | [1, 1, 1] | 1 | - |
| 28687 | 同关卡隔热材料 | sm_l13_gerecailiao.prefab | Box [1.19, 0.1, 1.19] (+2个) | [0, 0.05, 0] (轴心在底部) | - | - | [1, 1, 1] | 4 | - |
| 28688 | 带解锁区域 | sm_l13_djsqy.prefab | Box [3.53, 0.16, 3.53] (+15个) | [0, 0.08, 0] (轴心在底部) | - | - | [1, 1, 1] | 16 | - |
| 28694 | 零件3 | sm_l13_lingjian_03.prefab | Box [0.04, 0.09, 0.04] | [0, 0.04, 0] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 28695 | 零件1 | sm_l13_lingjian_01.prefab | Box [0.05, 0.09, 0.05] | [0, 0.04, 0] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 28696 | 零件2 | sm_l13_lingjian_02.prefab | Box [0.04, 0.09, 0.03] | [0, 0.04, 0] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 28697 | 能源存放箱 绿色 | sm_l15_nycfx_02.prefab | Box [-1.37, 0.8, 1.17] | [0, 0.38, 0.06] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 28698 | 能源存放箱 红色 | sm_l15_nycfx_01.prefab | Box [-1.37, 0.8, 1.17] | [0, 0.38, 0.06] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 28699 | 扁易拉罐 | sm_l15_pylg.prefab | Box [0.15, 0.18, 0.17] | [-0.01, 0.09, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28700 | 香蕉皮 | sm_l15_xjp.prefab | Box [0.37, 0.26, 0.4] | [0, 0.13, 0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28737 | 影子 | sm_l13_yingzi.prefab | Box [10, 0, 10] | [0, 0, 0] | 静态×2 | - | [1, 1, 1] | 1 | - |
| 28738 | 一篮子土块 | sm_l15_yltk.prefab | Box [1.22, 1.17, 1.22] | [0, 0.59, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28740 | 小版组装材料版 | sm_l13_mianbandui01a02.prefab | 无 | - | - | - | [1, 1, 1] | 0 | - |
| 28744 | 垃圾堆 | sm_l15_ljd.prefab | Box [2.63, 1.33, 1.9] | [-0.06, 0.59, 0.13] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 28748 | 关卡 太阳能板 | sm_l13_taiyangnengban.prefab | 无 | - | - | - | [1, 1, 1] | 1 | - |
| 28749 | 陨石 | sm_l13_yunshi.prefab | Box [0.49, 0.48, 0.32] Trigger | [-0.03, 0.24, -0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28754 | 神经 | sm_l14_shenjing.prefab | Box [0.6, 0.66, 1.02] | [-0.14, 0.18, 0.55] (轴心偏移) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 28936 | 桌子01-关卡 | sm_l13_zhuozi01.prefab | Box [11.62, 3.73, 6.58] | [0, 1.91, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28937 | 桌子02-关卡 | sm_l13_zhuozi02.prefab | Box [8.94, 3.3, 1.94] | [0, 1.65, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28938 | 桌子03-关卡 | sm_l13_zhuozi03.prefab | Box [9.68, 4.71, 1.82] | [0, 2.35, -0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28952 | 出库机 | sm_l14_ckj.prefab | Box [3.64, 2.2, 3.33] | [-0, 1.1, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28989 | 机械寄生体 | sm_l14_jxjst.prefab | Box [0.22, 0.22, 0.22] | [0, 0.17, 0] (轴心偏下) | - | - | [1, 1, 1] | 0 | - |
| 28996 | 核心材料 | sm_L13_hexincailiao.prefab | Box [0.42, 0.22, 0.42] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 28999 | 全向车机械臂货框颜色传感器 | jixiebiquanxiangche_jixiebi_huowukuai.prefab | Box [9.5, 5, 8] | [0, 2.25, -1.22] (轴心在底部) | 蒙皮×5 / 静态×1 | songjiazhua, kaijiazhua(1.00s,一次), guanbijiazhua(2.00s,一次), jiahuowu | [1, 1, 1] | 21 | - |
| 29009 | 降维陨石碎片 | jiangweiyunshi_suipian.prefab | Box [1, 1, 1] | [0, 1.25, 0] (轴心偏下) | - | idle(2.00s,循环) | [1, 1, 1] | 0 | - |
| 29110 | 检测机器 | SM_pingjijiqiz_a01.prefab | Box [2.69, 2.48, 2.35] | [-0, 1.24, -0.16] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29111 | 脑电波机 | hemunaodianboji.prefab | Box [4.37, 6.79, 5.06] | [0.01, 3.19, 0.1] (轴心在底部) | - | idle(2.00s,循环) | [1, 1, 1] | 1 | - |
| 29136 | 测试灰地砖 | sm_l13_huidizhuan.prefab | Box [2.61, 0.28, 2.61] | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29137 | 测试灰地砖02 | sm_l13_huidizhuan02.prefab | Box [2.61, 0.28, 2.61] | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29138 | 矿洞大门 密码锁 | sm_l15_kdmms_01.prefab | Box [1.24, 0.65, 0.29] | [-0.19, 0.71, 0.06] (轴心偏下) | - | - | [1, 1, 1] | 1 | - |
| 29139 | 新 核心材料 | sm_L14_hexincailiao.prefab | Box [0.22, 0.08, 0.22] | [-0, 0.07, 0] (轴心偏下) | - | - | [1, 1, 1] | 2 | - |
| 29140 | 窑炉    窑炉口1 | sm_l15_yaoluko.prefab | Box [11.4, 10.47, 10.64] (+1个) | [-0.12, 5.55, 0.02] (轴心在底部) | 蒙皮×1 / 粒子×1 | - | [1, 1, 1] | 4 | - |
| 29141 | 窑炉口2 | sm_l15_yaoluko02b.prefab | Box [2.24, 2.61, 1] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29157 | 窑炉口 | sm_l15_fenleijiqi.prefab | Box [1.95, 1.6, 1.92] | [0, 0.75, 0] (轴心在底部) | - | penqi(2.00s,一次), idle(0.03s,一次) | [1, 1, 1] | 1 | - |
| 29160 | 石墨烯避雷针塔 01 | sm_l14_blzt_hei_01.prefab | Box [0.32, 2.63, 0.32] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1.13, 1, 1.13] | 1 | - |
| 29225 | 传送履带 | sm_chuansonglvdai01.prefab | Box [0.58, 0.41, 2.25] | [0, 0.2, -0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29227 | 挂衣架 | sm_L15_guayijia.prefab | Box [2.65, 1.71, 0.42] | [0, 0.86, 0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29228 | 防爆盾牌 | sm_l14_fangbaodunpai.prefab | Box [0.46, 1.22, 0.08] | [0, 0.61, -0.01] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29243 | 分割机器 | fengejiqi.prefab | Box [1.95, 1.6, 1.92] | [0, 0.75, 0] (轴心在底部) | - | idle(0.03s,一次), penqi(2.00s,一次) | [1, 1, 1] | 0 | - |
| 29247 | 新隔热材料 | sm_l13_gerecailiao02.prefab | Box [10, 0, 10] (+3个) | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 5 | - |
| 29265 | 盲盒 | manghe.prefab | Box [1.2, 1.2, 1.2] | [0, 0.5, 0] (轴心在底部) | - | idle(0.03s,一次), dakai(0.67s,一次), dakai_loop(0.03s,一次) | [1, 1, 1] | 0 | - |
| 29269 | 火药 堆状 | sm_l15_hy.prefab | Box [1.85, 1, 1.82] | [0, 0.43, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29270 | 凝胶弹 | sm_l15_njd.prefab | Box [0.68, 1.24, 0.67] | [0, 0.58, -0.03] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29275 | 物资箱打开 | wuzixiang_daidonghua_dakai.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | idle | [1, 1, 1] | 1 | - |
| 29276 | 物资箱打开02 | wuzixiang_daidonghua02_dakai.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | idle | [1, 1, 1] | 1 | - |
| 29290 | 食物箱 | wuzixiang_shiwu.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | dakai_idle(1.00s,循环), bihe_idle(1.00s,循环), dakai, bihe | [1, 1, 1] | 1 | - |
| 29291 | 食物箱打开状态 | wuzixiang_shiwu_dakai.prefab | Box [1.36, 1.4, 1] | [0.01, 0.69, 0] (轴心在底部) | - | idle | [1, 1, 1] | 1 | - |
| 29292 | 脑电波机屏幕 | sm_l4_ndbj_01.prefab | Box [2.88, 1.6, 0.61] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 1 | - |
| 29293 | 脑电波机底座 | sm_l4_ndbj_02.prefab | Box [4.46, 1.57, 2.45] | [0, 0.7, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 29297 | 漫波神庙大门 | manboshenmiao_damen.prefab | Box [18, 19, 15] | [0, 8.5, 0] (轴心在底部) | 蒙皮×5 / 粒子×6 | dakai(2.33s,一次), dakai_loop(0.03s,一次), guanbi(0.03s,一次) | [1, 1, 1] | 23 | - |
| 29298 | 漫波大神庙密码门 | manbodashenmiao_mimamen.prefab | Box [18, 19, 15] | [0, 8.5, 0] (轴心在底部) | 蒙皮×6 / 粒子×6 | guanbi(0.03s,一次), dakai(1.37s,一次), dakai_loop(0.03s,一次) | [1, 1, 1] | 18 | - |
| 29299 | 切割机器 | qiegejiqi.prefab | Box [1.65, 1.5, 1.3] | [0, 0.7, 0] (轴心在底部) | - | dakai(1.63s,一次), guanbi(0.03s,一次), dakai_loop(0.67s,循环) | [1, 1, 1] | 1 | - |
| 29301 | 榴莲 | sm_l14_liulian.prefab | Box [0.38, 0.45, 0.38] | [0, 0.23, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29304 | 漫波控制台 | sm_l15_mbkzt.prefab | Box [2.85, 2.8, 1.78] | [0, 1.34, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29314 | 树脂 | sm_l14_shuzhi.prefab | Box [0.46, 0.54, 0.4] | [0, 0.27, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29315 | 硼砂 | sm_l14_pengsha.prefab | Box [0.49, 0.48, 0.32] | [-0.03, 0.24, -0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29316 | 合金材料 | sm_l14_hjcl.prefab | Box [0.6, 0.6, 2.09] | [0, 0.23, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 29317 | 大型科幻箱 | sm_l14_khx.prefab | Box [1.76, 2.26, 1.46] | [0, 0.69, 0.52] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 29333 | 计时器 | sm_l14_jshiqi.prefab | Box [0.2, 0.19, 0.05] | [0, 0.1, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29334 | 钟表 | zhongbiao.prefab | Box [0.8, 0.75, 0.5] | [0, 0.35, 0] (轴心在底部) | - | 6dian(0.03s,一次), 10dian(0.03s,一次), zhuan(2.00s,一次) | [1, 1, 1] | 0 | - |
| 29335 | 铝合金01 | sm_l14_lv_01.prefab | Box [4.29, 1, 3.6] | [0, 0.39, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29336 | 铝合金 短 | sm_l14_lv_02.prefab | Box [1.37, 0.38, 1.69] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29337 | 硅合金01 | sm_l14_gui_01.prefab | Box [4.29, 1, 3.6] | [0, 0.39, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29338 | 硅合金 短 | sm_l14_gui_02.prefab | Box [1.37, 0.38, 1.69] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29339 | 铜合金01 | sm_l14_tong_01.prefab | Box [4.29, 1, 3.6] | [0, 0.39, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29340 | 铜合金 短 | sm_l14_tong_02.prefab | Box [1.37, 0.38, 1.69] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29344 | 铝合金 中 | sm_l14_lv_03.prefab | Box [1.37, 0.38, 2.86] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29345 | 铝合金 长 | sm_l14_lv_04.prefab | Box [1.37, 0.38, 4.37] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29347 | 硅合金 中 | sm_l14_gui_03.prefab | Box [1.37, 0.38, 2.86] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29348 | 硅合金 长 | sm_l14_gui_04.prefab | Box [1.37, 0.38, 4.37] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29349 | 铜合金 中 | sm_l14_tong_03.prefab | Box [1.37, 0.38, 2.86] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29350 | 铜合金 长 | sm_l14_tong_04.prefab | Box [1.37, 0.38, 4.37] | [0, 0.12, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29353 | 防毒材料堆 | sm_l14_fdcld_01.prefab | Box [8.39, 1.53, 8.43] | [1.73, 0.29, -0.33] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29354 | 漫波记忆硬盘 | sm_l14_mbjyyp_01.prefab | Box [0.31, 0.21, 0.51] | [0, 0.07, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29359 | 岩浆发电机 | sm_l14_fadianji.prefab | Box [10.32, 6.85, 10.32] Trigger (+1个) | [0, 3.94, 0] (轴心在底部) | - | - | [1, 1, 1] | 3 | - |
| 29632 | 岩浆发电机封锁版 | sm_l14_fadianjifengsuo.prefab | Box [6.64, 6.64, 6.64] | [0, 3.35, 0] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29633 | 马车 | sm_l14_mache01.prefab | Capsule r=0.85,h=2.9 (+4个) | [0, 1.4, 0] | 静态×1 | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 5 | 其它脚本×1 |
| 29637 | 榴莲 | liulian.prefab | Box [0.89, 0.9, 0.9] | [0, 0.45, 0] (轴心在底部) | - | dakai(1.00s,一次), dakai_loop(0.03s,一次), bihe(0.03s,一次) | [1, 1, 1] | 1 | - |
| 29638 | 榴莲坏了 | liulian_huai.prefab | Box [0.89, 0.9, 0.9] | [0, 0.45, 0] (轴心在底部) | - | dakai(1.00s,一次), dakai_loop(0.03s,一次), bihe(0.03s,一次) | [1, 1, 1] | 1 | - |
| 29649 | super钻头 | sm_l14_zuantou.prefab | Box [0.18, 0.74, 0.17] | [0, 0.37, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29650 | 绝缘体装甲片 | sm_l15_jiapian.prefab | Box [0.93, 0.27, 1.06] | [0, 0.13, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29651 | EMP | sm_l15_emp.prefab | Box [1.98, 1.69, 0.6] | [0, 0.88, -0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29661 | 曼德拉草_捕狼草 | mandelacao_3Djingling_bulangcao.prefab | Box [1, 1.65, 1] (+1个) | [0, 0.85, 0] (轴心在底部) | 静态×1 | jianjiao, dishang_idle(1.33s,循环), dixia_idle(1.33s,循环) | [1, 1, 1] | 5 | 其它脚本×2 |
| 29663 | 商人货车白 | sm_l14_mache03.prefab | Capsule r=0.85,h=2.9 (+4个) | [0, 1.4, 0] | 静态×1 | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 5 | 其它脚本×1 |
| 29664 | 商人货车黑 | sm_l14_mache02.prefab | Capsule r=0.85,h=2.9 (+4个) | [0, 1.4, 0] | 静态×1 | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 5 | 其它脚本×1 |
| 29665 | 休眠舱-休眠状态 | sm_l15_xiumiancang.prefab | Box [2.08, 2.08, 1.44] (+1个) | [0, 1.89, -0.33] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 29666 | 地砖  红 | sm_l15_dizhuan.prefab | Box [2.61, 0.28, 2.61] | [0, 0.14, 0] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 29671 | 配置机器 履带 | sm_l14_pzjq_02.prefab | Box [4.56, 0.48, 1.35] | [1.63, 0.23, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 29672 | 配置机器 机身 | sm_l14_pzjq.prefab | Box [2.34, 2.91, 2.21] | [-0.22, 1.37, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 29674 | 空货架摊 | sm_gk_konghuojiatan.prefab | Box [5.17, 3.54, 3.28] (+3个) | [0, 1.71, 0] (轴心在底部) | - | - | [1, 1, 1] | 4 | - |
| 29675 | 护卫机甲 | sm_gk_mofarenou1.prefab | Box [2.37, 1.02, 1.8] (+1个) | [0, -0.06, 0.9] (轴心居中) | 静态×1 | daodi_loop, aida, walk(1.53s,循环), idle(1.60s,循环), run(1.13s,循环), dance_loop, lunquan | [1, 1, 1] | 5 | 其它脚本×1 |
| 29801 | 弹坑 | sm_l15_dankeng.prefab | Box [3.63, 1.19, 3.74] | [0, 0.52, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29804 | 马车黄色无货物 | mache_huang_wuhuo.prefab | Box [9, 3, 2.62] | [2.9, 1.5, 0] (轴心在底部) | - | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 1 | - |
| 29805 | 马车黄色有货物 | mache_huang_youhuowu.prefab | Box [9, 3, 2.62] (+1个) | [2.9, 1.5, 0] (轴心在底部) | 静态×1 | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 29806 | 马车白色无货物 | mache_bai_wuhuo.prefab | Box [9, 3, 2.62] | [2.9, 1.5, 0] (轴心在底部) | - | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 1 | - |
| 29807 | 马车白色有货物 | mache_bai_youhuowu.prefab | Box [9, 3, 2.62] (+1个) | [2.9, 1.5, 0] (轴心在底部) | 静态×1 | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 29808 | 马车黑色无货物 | mache_hei_wuhuo.prefab | Box [9, 3, 2.62] | [2.9, 1.5, 0] (轴心在底部) | - | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 1 | - |
| 29809 | 马车黑色有货物 | mache_hei_youhuowu.prefab | Box [9, 3, 2.62] (+1个) | [2.9, 1.5, 0] (轴心在底部) | 静态×1 | walk, masi, idle(1.60s,循环), run(0.67s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 29815 | 漫波灭火器 | sm_L14_miehuoqi.prefab | Box [0.24, 0.85, 0.35] | [0, 0.43, 0.01] (轴心在底部) | - | - | [1, 1, 1] | 1 | - |
| 29816 | 无人机携带漫波灭火器 | sm_gk_wrjmhq.prefab | Box [0.24, 0.85, 0.35] | [0, 0.43, 0.01] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 29817 | 火堆 | sm_gk_huodui.prefab | Box [0.92, 0.19, 4.11] (+7个) | [0, 0.09, 0] (轴心在底部) | - | - | [1, 1, 1] | 9 | - |
| 29819 | 灰尘 01 | sm_l14_shadui_01.prefab | Box [6.1, 0, 6.1] (+1个) | [0, 0, 0] | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29820 | 灰尘 02 | sm_l14_shadui_02.prefab | Box [4.08, 0.98, 4.59] (+1个) | [0.41, 0.49, 0.12] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29821 | 曼波塔 | manbota.prefab | Box [1, 1.2, 1] (+1个) | [0, 0.55, 0] (轴心在底部) | 静态×1 | run02(0.47s,循环), kaiji, fakuang(1.80s,循环), kaijishibai, zhanli_idle, idle, run(0.53s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 29824 | 数字密码锁 设计说明书 | sm_l14_sjsms.prefab | Box [0.3, 0, 0.4] | [0, 0, 0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29825 | 冰冻白菜堆 | sm_l14_bdbc.prefab | Box [1.18, 0.56, 2.69] | [0, 0.15, -0.42] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 29826 | 肥料堆 | sm_l14_feiliao.prefab | Box [0.57, 0.41, 0.28] | [0.14, 0.16, -0.05] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 29827 | 压缩饼干 | sm_L14_yasuobinggan.prefab | Box [0.52, 0.13, 0.3] (+1个) | [-0.01, 0.07, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29828 | 医药包 | sm_L14_yiyaobao.prefab | Box [0.75, 0.74, 0.31] | [0.02, 0.37, 0.02] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29829 | 盒装镇定剂 | sm_L14hezhuangzhendingji.prefab | Box [0.74, 1.31, 0.4] | [-0.02, 0.5, 0.15] (轴心在底部) | - | - | [1, 1, 1] | 2 | - |
| 29830 | 门禁卡 | sm_l14_mjk.prefab | Box [0.46, 0.38, 0] | [0, 0, -0] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29831 | 麦穗堆 | sm_l14_maisui.prefab | Box [2.04, 0.54, 1.36] | [-0.25, 0, -0.39] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 29832 | 核心电池 单个核心电池 | sm_I14_hxdianchi_01.prefab | Box [1.92, 1.58, 0.84] | [0, 0.46, 0] (轴心偏移) | - | - | [1, 1, 1] | 1 | - |
| 29833 | 核心电池堆 | sm_I14_hxdianchi_02.prefab | Box [0.59, 0.59, 0.84] | [0, 0, 0] (轴心居中) | - | - | [1, 1, 1] | 0 | - |
| 29834 | 休眠舱 | xiumiancang.prefab | Box [2, 4, 2] | [0, 1.9, 0] (轴心在底部) | - | dakai_loop(0.03s,一次), dakai(1.67s,一次), idle(0.03s,一次) | [1, 1, 1] | 0 | - |
| 29841 | 一堆金币 | sm_l14_ydjb.prefab | Box [6.54, 1.48, 6.12] | [0, 0.67, -0.37] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 29842 | 小鸡的装药碗 | sm_l14_zhuangyaowan.prefab | Box [0.76, 0.26, 0.76] | [-0.06, 0.15, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29929 | 小鸡吃的药 一份 | sm_l14_xiaojiyao_01.prefab | Box [0.8, 0.21, 0.78] | [0, 0.09, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 29930 | 小鸡吃的药 三份 | sm_l14_xiaojiyao_02.prefab | Box [2.19, 0.38, 1.79] | [0.4, 0.13, 0.32] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 29931 | 小鸡吃的药 五份 | sm_l14_xiaojiyao_03.prefab | Box [2, 0.51, 2.01] | [0.49, 0.19, 0.48] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 29932 | 小鸡吃的药 多份 | sm_l14_xiaojiyao_04.prefab | Box [2.89, 0.94, 3.33] | [0.49, 0.19, 0.09] (轴心偏移) | - | - | [1, 1, 1] | 0 | - |
| 29933 | 红土块 | sm_l15_hongtukuai.prefab | Box [1.22, 1.17, 1.22] | [0, 0.59, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29934 | 黑土块 | sm_l14_heitukuai.prefab | Box [0.46, 0.54, 0.4] Trigger | [0, 0.27, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 29935 | 煤球2 | sm_l15_meikuai2.prefab | Mesh | - | 静态×1 | - | [1, 1, 1] | 1 | - |
| 29936 | 煤球7 | sm_l15_meikuai7.prefab | Mesh | - | 静态×1 | - | [1, 1, 1] | 1 | - |
| 30101 | 碎盲盒 | sm_l14_smh.prefab | Box [2.99, 1, 2.22] | [-0.1, 0.08, 0.13] (轴心居中) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 30105 | no箱 | sm_l14_xiangzi_no.prefab | Box [1.35, 0.93, 1.69] | [-0.06, 0.48, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 30106 | yes箱 | sm_l14_xiangzi.prefab | Box [1.35, 0.93, 1.69] | [-0.06, 0.48, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 30107 | 传送带 | sm_l14_csd.prefab | Box [1.21, 0.39, 4.32] (+1个) | [0, 0.23, 0] (轴心在底部) | 静态×2 | - | [1, 1, 1] | 3 | - |
| 30108 | 评级机器关卡 | sm_gk_pjjq.prefab | Box [2.57, 2.48, 2.76] | [-0.05, 1.24, 0] (轴心在底部) | - | penqi(2.00s,一次), idle(0.03s,一次) | [1, 1, 1] | 3 | - |
| 30109 | 贴标签机器 | sm_gk_tbqjq.prefab | Box [1.23, 2.75, 2.01] (+1个) | [0.06, 1.37, 0] (轴心在底部) | - | - | [1, 1, 1] | 3 | - |
| 30110 | 炮弹加工机器 | sm_gk_pdjgjq.prefab | Box [2.27, 1.52, 1.91] (+2个) | [0, 0.83, 0] (轴心在底部) | - | - | [1, 1, 1] | 4 | - |
| 30111 | 胶囊存储器 | jiaonangchucunqi.prefab | Box [0.5, 1, 0.5] | [0, 0.35, 0] (轴心偏移) | - | dakai(0.67s,一次), idle(0.03s,一次), dakai_loop(0.03s,一次) | [1, 1, 1] | 1 | - |
| 30189 | 小核桃emp | xiaohetao_emp.prefab | Box [1, 2, 0.79] (+1个) | [0, 0.97, 0] (轴心在底部) | 静态×1 | youshoudianji, idle(1.73s,循环), zuoshoujuqi, shurumima | [1, 1, 1] | 5 | 其它脚本×1 |
| 30192 | 普通炮弹 | sm_l14_ptpd.prefab | Box [0.6, 1.16, 0.59] | [0, 0.59, -0.04] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 30305 | 漫波塔说明书 | sm_l15_mbsms.prefab | Box [0.62, 0.42, 0.12] | [0, 0.21, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 30306 | 矿泉水 | sm_l15_ljd_08.prefab | Box [0.12, 0.29, 0.12] | [0, 0.14, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 30435 | 食物箱150 | wuzixiang_150.prefab | Box [2.02, 1.4, 1.71] | [0.01, 0.69, 0] (轴心在底部) | - | dakai_idle(1.00s,循环), bihe_idle(1.00s,循环), dakai, bihe | [1, 1, 1] | 1 | - |
| 30436 | 物资箱150堆叠 | wuzixiang_150duidie.prefab | Box [2.02, 1.4, 1.71] | [0.01, 0.69, 0] (轴心在底部) | - | dakai_idle(1.00s,循环), bihe_idle(1.00s,循环), dakai, bihe | [1, 1, 1] | 5 | - |
| 30437 | 遗迹口大门 | yijikoudamen.prefab | Box [9, 9, 4.45] | [0, 4, 0] (轴心在底部) | - | dakai(1.33s,一次), guanbi(0.03s,一次), dakai_loop(0.03s,一次) | [1, 1, 1] | 1 | - |
| 30455 | 榴莲大炮 | sm_l14_lldp.prefab | Box [2.38, 2.74, 3.64] | [0, 1.29, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 1 | - |
| 30459 | 胶囊存储器 | sm_L14_jiaonangchucunqi.prefab | Box [0.21, 0.29, 0.21] Trigger (+1个) | [0, 0.34, 0] (轴心偏下) | 静态×2 | - | [1, 1, 1] | 2 | - |
| 30472 | 红土块02 | sm_l15_htk.prefab | Box [93.04, 96.99, 81.61] | [-1.88, 54.01, 0.46] (轴心在底部) | 静态×1 | - | [0.01, 0.01, 0.01] | 1 | - |
| 30473 | 一篮子石墨 | sm_gk_ylzsm.prefab | 无 | - | 静态×1 | - | [1, 1, 1] | 2 | - |
| 30474 | yes箱子 | sm_gk_xiangzi_yes.prefab | Mesh (+1个) | - | 静态×2 | - | [1, 1, 1] | 2 | - |
| 30475 | no箱子 | sm_gk_xiangzi_no.prefab | Mesh (+1个) | - | 静态×2 | - | [1, 1, 1] | 2 | - |
| 30550 | 钟表空白 | zhongbiao_kongbai.prefab | Box [0.8, 0.75, 0.5] | [0, 0.35, 0] (轴心在底部) | - | - | [1, 1, 1] | 0 | - |
| 30670 | 曼波塔趴地上 | manbota_padi.prefab | Box [1, 1.2, 1] (+1个) | [0, 0.55, 0] (轴心在底部) | 静态×1 | run02(0.47s,循环), kaiji, fakuang(1.80s,循环), kaijishibai, zhanli_idle, idle, run(0.53s,循环) | [1, 1, 1] | 4 | 其它脚本×1 |
| 30823 | 冰沙  粉色 | sm_l16_bingsha_fen.prefab | Box [0.35, 0.66, 0.31] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 30824 | 冰沙  黄色 | sm_l16_bingsha_huang.prefab | Box [0.35, 0.66, 0.31] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 30825 | 冰沙  蓝色 | sm_l16_bingsha_lan.prefab | Box [0.35, 0.66, 0.31] | [0, 0.33, 0] (轴心在底部) | 静态×1 | - | [1, 1, 1] | 0 | - |
| 30844 | 营地大仓库 | sm_l16_dck.prefab | 未找到prefab | - | - | - | - | - | - |

## 资源追溯：物件 → Mesh / Material / Texture

> `源FBX` 是 MeshFilter / SkinnedMeshRenderer 引用的几何体文件；`材质` 是 prefab 引用的 .mat 数；`贴图` 是逐个 .mat 追到的主贴图文件名（去重）。

| AssetId | 名称 | 源FBX (相对 meishu) | 材质数 | 贴图 |
|---------|------|---------------------|--------|------|
| 10167 | 立体路径 | model/prop/box.fbx | 1 | box_D.tga |
| 12391 | 煤球道具 | model/prop/BigWorld/L1/meiqiu/meiqiu.fbx | 1 | meiqiu_D.png |
| 12582 | 宝箱 | model/player/baoxiang/baoxiang@skin.fbx | 2 | shadows.png, zhuo_D(2).tga |
| 12583 | 领奖台 | model/prop/BigWorld/L2/jiuyou/024.FBX | 1 | 2.psd |
| 12586 | 钥匙 | model/prop/BigWorld/L2/jiuyou/018.FBX | 1 | 2.psd |
| 12588 | 普通机械螃蟹 | - | 1 | shadows.png |
| 12945 | 九婴体内牌子 | model/prop/BigWorld/L2/jiuyou/010.FBX | 1 | 2.psd |
| 13007 | 一片草丛 | model/common/Model/SM_cao_a.FBX<br>model/common/Model/SM_cao_b.FBX | 1 | T_cao_a.tga |
| 13009 | 书 | model/sprite3d/SM_book.FBX | 1 | T_book.tga |
| 13011 | 评级机器02 | model/sprite3d/SM_pingjijiqiz_b.FBX | 1 | T_pingjijiqi.png |
| 13012 | 食人花 | model/sprite3d/SM_rafflesia.FBX | 1 | T_rafflesia.png |
| 13013 | 钥匙 | model/sprite3d/SM_yaoshi.FBX | 1 | T_yaoshi.png |
| 13014 | 锻造材料01 | model/sprite3d/SM_lianzaocailiao_01.FBX | 1 | T_lianzaocailiao.png |
| 13015 | 锻造材料02 | model/sprite3d/SM_lianzaocailiao_02.FBX | 1 | T_lianzaocailiao.png |
| 13016 | 锻造材料03 | model/sprite3d/SM_lianzaocailiao_03.FBX | 1 | T_lianzaocailiao.png |
| 13017 | 一篮煤球 | model/sprite3d/SM_yilanmeiqiu.FBX | 1 | T_lianzaocailiao.png |
| 13310 | 分流机器01 | model/sprite3d/SM_fenliujiqi_a.FBX | 1 | T_fenliujiqi.png |
| 13311 | 分流机器02 | model/sprite3d/SM_fenliujiqi_b.FBX | 1 | T_fenliujiqi.png |
| 13344 | 桌子 | model/C1/L1/Model/L1_03_04/sm_tavern_object_02_i.FBX | 1 | t_tavern_object_02.png |
| 14516 | 茶杯展示架 | model/sprite3d/sm_jiazi.FBX | 1 | t_daoju_01.png |
| 14517 | 海茉莉 | model/sprite3d/sm_haitanghua_01.fbx | 1 | t_haitanghua_01.png |
| 14518 | 陷阱 | model/sprite3d/sm_traps_01.FBX | 1 | t_daoju_02.png |
| 14519 | 红外遥控器 | model/sprite3d/sm_yaokongqi.FBX | 1 | t_daoju_02.png |
| 14640 | 蜜雪冰牛奶茶粉 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_fen.fbx | 1 | t_daoju_mixuebingniu_D.png |
| 14641 | 蜜雪冰牛奶茶黄 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_huang.fbx | 1 | t_daoju_mixuebingniu_D.png |
| 14642 | 蜜雪冰牛奶茶蓝 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_lan.fbx | 1 | t_daoju_mixuebingniu_D.png |
| 14643 | 蜜雪冰牛奶茶绿 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_lv.fbx | 1 | t_daoju_mixuebingniu_D.png |
| 14644 | 棍棒 | model/C1/L2/Model/L2_01_01/sm_langyabang.fbx | 1 | t_daoju_D.png |
| 14645 | 草叉 | model/C1/L2/Model/L2_01_01/sm_yucha.fbx | 1 | t_daoju_D.png |
| 14646 | 马桶撅 | model/C1/L2/Model/L2_01_01/sm_matongsai.fbx | 1 | t_daoju_D.png |
| 14647 | 木牌 | model/C1/L2/Model/L2_01_01/sm_lupai.FBX | 1 | t_daoju_02.png |
| 14648 | 桌子 | model/C1/L2/Model/L2_01_01/sm_zhuozi.FBX | 1 | t_daoju_02.png |
| 14649 | 昆仑灵芝 | model/C1/L2/Model/L2_01_01/sm_lingzhi_01.FBX | 1 | t_lingzhi.png |
| 14651 | 天山雪莲 | model/C1/L2/Model/L2_01_01/sm_lianhua.FBX | 1 | t_daoju_02.png |
| 14652 | 特制炼丹鼎 | model/C1/L2/Model/L2_01_01/sm_ding.FBX | 1 | t_daoju_01.png |
| 14653 | 九转还魂丹 | model/C1/L2/Model/L2_01_01/sm_qiu.FBX | 1 | t_daoju_02.png |
| 14654 | 珍珠竹筐 | model/C1/L2/Model/L2_01_01/sm_zhukuang.fbx | 1 | zhukuang.png |
| 14655 | 红豆竹筐 | model/C1/L2/Model/L2_01_01/sm_zhukuang.fbx | 1 | zhukuang.png |
| 14656 | 椰果竹筐 | model/C1/L2/Model/L2_01_01/sm_zhukuang.fbx | 1 | zhukuang.png |
| 14668 | 海州衙门桌子 | model/C1/L2/Model/L2_01_01/sm_haizhouyamen_xiaowujian04.FBX | 1 | t_haizhou_yamen_04.png |
| 14670 | 绿桌子 | model/C1/L2/Model/L2_01_01/sm_zhuozi.FBX | 1 | t_daoju_02.png |
| 14671 | 被污染的昆仑灵芝 | model/C1/L2/Model/L2_01_01/sm_lingzhi_02.FBX | 1 | t_lingzhi.png |
| 14677 | 八面玲珑眼 | model/sprite3d/sm_daoju_maoleida.fbx | 2 | t_daoju_maoleida_shenti.png, t_daoju_maoleida_yan.png |
| 14680 | 猫雷达 | - | 1 | shadows.png |
| 14721 | 黄牛_3D | - | 1 | shadows.png |
| 14722 | 队长_3D | - | 1 | shadows.png |
| 14723 | 展喵_3D | - | 1 | shadows.png |
| 14724 | 小核桃_3D | - | 1 | shadows.png |
| 14725 | 核桃机甲_3D | - | 1 | shadows.png |
| 14727 | 茶杯盖子 | - | 1 | shadows.png |
| 14728 | 金光宝石（正常状态） | model/sprite3d/sm_l3_jinguangbaoshi.fbx | 1 | t_l3_daoju.png |
| 14729 | 金光宝石（强光状态） | model/sprite3d/sm_l3_jinguangbaoshi.fbx | 1 | t_l3_daoju.png |
| 14730 | 海蓝宝石（正常状态） | model/sprite3d/sm_l3_hainanbaoshi.fbx | 1 | t_l3_daoju.png |
| 14731 | 海蓝宝石（强光状态） | model/sprite3d/sm_l3_hainanbaoshi.fbx | 1 | t_l3_daoju.png |
| 14732 | 鉴宝机 | model/sprite3d/sm_l3_jianbaoji.fbx | 1 | t_l3_jianbaoji.png |
| 14733 | 龟壳打印机01 | model/sprite3d/sm_l3_wuguidayinji_01.fbx | 1 | t_l3_wuguidayinji.png |
| 14734 | 龟壳打印机02 | model/sprite3d/sm_l3_wuguidayinji_02.fbx | 1 | t_l3_wuguidayinji.png |
| 14735 | 龟壳打印机03 | model/sprite3d/sm_l3_wuguidayinji_03.fbx | 1 | t_l3_wuguidayinji.png |
| 14736 | 龟壳打印机04 | model/sprite3d/sm_l3_wuguidayinji_04.fbx | 1 | t_l3_wuguidayinji.png |
| 14737 | 景王喂食机1号 | model/sprite3d/sm_l3_jiingwangweishiji_01.fbx | 1 | t_l3_jiingwangweishiji.png |
| 14738 | 景王喂食机2号 | model/sprite3d/sm_l3_jiingwangweishiji_02.fbx | 1 | t_l3_jiingwangweishiji.png |
| 14739 | 景王种植机 | model/sprite3d/sm_l3_zhongzhiji.fbx | 1 | t_l3_zhongzhiji.png |
| 14758 | 破船 | model/sprite3d/sm_l3_pochuan.fbx | 1 | t_l3_pochuan.png |
| 14759 | 好船 | model/sprite3d/sm_l3_haochuan_01.fbx | 2 | t_l3_haochuan.png, t_l3_haochuan_02.png |
| 14761 | 密室大门 | model/sprite3d/sm_l3_mimasuo_damen.fbx | 2 | t_l3_zhifu_qiang_01.png, t_l3_zhifu_01.png |
| 15074 | 密码锁1 | model/sprite3d/sm_l3_mimasuo_06.fbx | 1 | t_l3_zhifu_01.png |
| 15075 | 密码锁2 | model/sprite3d/sm_l3_mimasuo_05.fbx | 1 | t_l3_zhifu_01.png |
| 15076 | 密码锁3 | model/sprite3d/sm_l3_mimasuo_07.fbx | 1 | t_l3_zhifu_01.png |
| 15077 | 密码锁4 | model/sprite3d/sm_l3_mimasuo_08.fbx | 1 | t_l3_zhifu_01.png |
| 15078 | 密码锁（源代码化） | model/sprite3d/sm_l3_mimasuo_02.fbx | 1 | t_l3_zhifu_01.png |
| 15079 | 清道夫 | model/sprite3d/sm_l3_qingdaofu.fbx | 2 | t_l3_qingdaofu_yan.png, t_l3_qingdaofu_shenti.png |
| 15080 | 水瓶 | model/sprite3d/sm_l3_shuiping.fbx | 1 | t_l3_daoju.png |
| 15081 | 神秘宝石 （机关球） | model/sprite3d/sm_l3_shenmibaoshi.fbx | 1 | t_l3_daoju.png |
| 15082 | 碎布 | model/sprite3d/sm_l3_suibu.fbx | 1 | t_l3_daoju.png |
| 15188 | 智慧核心 | model/player/A1.1/zhihuihexin/sm_zhihui@skin.FBX | 5 | t_l1_daojuzhaopai.png, 20250321-094913.jpg, 20250321-094905.png, shadows.png, 20250321-094909.jpg |
| 15189 | 秋生账本 | model/sprite3d/sm_l3_qiushegnzhangben.fbx | 1 | t_l3_daoju.png |
| 15285 | 自动投喂机 | model/sprite3d/sm_l3_jiingwangweishiji_po.fbx | 1 | t_l3_jiingwangweishiji_po.png |
| 15286 | 密码手册 | model/sprite3d/sm_l3_mimashouce.fbx | 1 | t_l3_mimashouce.png |
| 15863 | 自动投喂机说明书 | model/sprite3d/sm_l3_shuomingshu.fbx | 1 | t_l3_jiingwangweishiji_po.png |
| 16086 | 蒙汗药01 | model/sprite3d/sm_kejianbuji_menghanyao_01.fbx | 1 | t_kejianbuji_xiaowujian.png |
| 16087 | 蒙汗药02 | model/sprite3d/sm_kejianbuji_menghanyao_02.fbx | 1 | t_kejianbuji_xiaowujian.png |
| 16363 | 防虫栅栏 | model/sprite3d/sm_l4_hulan.FBX | 1 | t_l4_hulan.png |
| 16383 | 虎身人面像 | model/sprite3d/sm_l4_baihu.fbx | 2 | t_l4_hushenrenmian_shenti.png, t_l4_hushenrenmian_zui.png |
| 16384 | pad | model/sprite3d/sm_l4_pad.fbx | 2 | t_l4_jinhuaxinpian_pingmu.png, t_l4_pad.png |
| 16385 | 蒸汽宝典 | model/sprite3d/sm_l4_zhengqibaodian.fbx | 2 | t_l4_zhengqibaodian.png, t_l4_zhengqibaodian_pingmu.png |
| 16386 | 进化芯片中 | model/sprite3d/sm_l4_jinhuaxinpian.fbx | 2 | t_l4_jinhuaxinpian_pingmu.png, t_l4_jinhuaxinpian.png |
| 16387 | 进化芯片小 | model/sprite3d/sm_l4_jinhuaxinpian.fbx | 2 | t_l4_jinhuaxinpian_pingmu.png, t_l4_jinhuaxinpian.png |
| 16388 | 兴奋薄荷的能量果实车 | model/sprite3d/sm_l4_daoju_qiche.FBX | 1 | t_l4_daoju_qiche.png |
| 16389 | 白菜的能量果实车 | model/sprite3d/sm_l4_daoju_qiche.FBX | 1 | t_l4_daoju_qiche.png |
| 16390 | 生命萝卜的能量果实车 | model/sprite3d/sm_l4_daoju_qiche.FBX | 1 | t_l4_daoju_qiche.png |
| 16391 | 防御椰子能量果实车 | model/sprite3d/sm_l4_daoju_qiche.FBX | 1 | t_l4_daoju_qiche.png |
| 16392 | 敏捷香蕉能量果实车 | model/sprite3d/sm_l4_daoju_qiche.FBX | 1 | t_l4_daoju_qiche.png |
| 16393 | 葫芦能量果实车 | model/sprite3d/sm_l4_daoju_qiche.FBX | 1 | t_l4_daoju_qiche.png |
| 16394 | 能源矿车 | model/sprite3d/sm_l4_daoju_chexiang.FBX | 1 | t_l4_daoju_chexiang.png |
| 16395 | 躺平西瓜 | model/sprite3d/sm_l4_bindongxigua.fbx | 1 | t_l4_bingdongxigua.png |
| 16396 | 碎石1 | model/C1/L3/Model/l3_01_01/sm_l3_jingwangfu_chitang_02.FBX | 1 | t_l3_jingwangfu_02.png |
| 16397 | 碎石2 | model/C1/L3/Model/l3_01_01/sm_l3_jingwangfu_chitang_03.FBX | 1 | t_l3_jingwangfu_02.png |
| 16398 | 碎石3 | model/C1/L3/Model/l3_01_01/sm_l3_jingwangfu_chitang_04.FBX | 1 | t_l3_jingwangfu_02.png |
| 16399 | 木牌子 | model/sprite3d/sm_l4_mupai.fbx | 1 | t_l4_mupaizi.png |
| 16400 | 梼杌（曾用名貔貅）大脚 | model/sprite3d/sm_l4_dajiao.fbx | 1 | t_l4_taowudajiao.png |
| 16401 | 梼杌（曾用名貔貅）大头 | model/sprite3d/sm_l4_datou.fbx | 1 | t_l4_taowudajiao.png |
| 16402 | 冰块碎石1 | model/sprite3d/sm_l4_suibing_01.FBX | 1 | t_l4_suibing.png |
| 16403 | 冰块碎石2 | model/sprite3d/sm_l4_suibing_02.FBX | 1 | t_l4_suibing.png |
| 16404 | 冰块碎石3 | model/sprite3d/sm_l4_suibing_03.FBX | 1 | t_l4_suibing.png |
| 16405 | 冰块碎石4 | model/sprite3d/sm_l4_suibing_04.FBX | 1 | t_l4_suibing.png |
| 16406 | 红温保安 | - | 1 | shadows.png |
| 16407 | 红温食人花 | - | 1 | shadows.png |
| 16408 | 红温扫地鲲 | - | 1 | shadows.png |
| 16409 | 红温机械狗仔 | - | 1 | shadows.png |
| 16410 | 红温螃蟹 | - | 1 | shadows.png |
| 16411 | 朱雀 | - | 1 | shadows.png |
| 16412 | 青龙 | model/sprite3d/sm_l4_qinglong.fbx | 2 | L4_qinglong_shenti_D.png, L4_qinglong_yan_D.png |
| 16413 | 白虎 | - | 1 | shadows.png |
| 16416 | 条幅 | model/sprite3d/sm_l4_hengfu_01.fbx | 1 | t_maobihengfu_01.png |
| 16417 | 纸张1 | model/sprite3d/sm_l4_feizhi_01.fbx | 1 | t_maobihengfu_01.png |
| 16418 | 纸张2 | model/sprite3d/sm_l4_feizhi_02.fbx | 1 | t_maobihengfu_01.png |
| 16419 | 毛笔 | model/sprite3d/sm_l4_maobi_01.fbx | 1 | t_maobihengfu_01.png |
| 16422 | 冰冻白菜 | model/sprite3d/sm_l4_bingdongbaicai.fbx | 1 | t_l4_bingdongxigua.png |
| 16423 | 芒果派 | model/sprite3d/sm_l4_mangguopai.fbx | 1 | t_l4_mangguopai.png |
| 16425 | 灯珠 | model/sprite3d/sm_l4_daoju_dengpai.FBX | 1 | t_l4_daoju_dengpai.png |
| 16427 | 算盘 | model/sprite3d/sm_l5_shanyangsuanpan.fbx | 1 | t_l5_gddpn_qiantai.png |
| 16428 | 圣旨 | model/sprite3d/sm_l5_shengzhi.FBX | 1 | t_l5_shengzhi.png |
| 16433 | 破烂喵朝军营帐篷 | model/sprite3d/sm_l5_hdzk_jianzhu_03_po.FBX | 1 | t_l5_hdzk_jianzhu_mao.png |
| 16437 | 降维陨石 | model/sprite3d/sm_l4_shibei_01.fbx | 1 | t_l4_shibei_01.png |
| 16455 | 地图碎片3 | model/sprite3d/sm_ditusuipian_03.fbx | 1 | t_l4_ditusuipian.png |
| 16456 | 地图碎片2 | model/sprite3d/sm_ditusuipian_02.fbx | 1 | t_l4_ditusuipian.png |
| 16457 | 地图碎片1 | model/sprite3d/sm_ditusuipian_01.fbx | 1 | t_l4_ditusuipian.png |
| 16458 | 桃源山全图 | model/sprite3d/sm_ditusuipian_02.fbx | 1 | t_l4_ditusuipian.png |
| 16956 | 星座壁画 | model/sprite3d/sm_l4_xingzuobihua.FBX | 1 | t_l4_xingzuobihua.png |
| 16975 | 雨滴传感器 | model/sprite3d/sm_l5_yudichuanganqi.FBX | 1 | t_l5_yudichuanganqi.png |
| 16976 | 蒸汽收银机 | model/sprite3d/sm_l5_zhengqishouyinji.FBX | 1 | t_l5_zhengqishouyinji.png |
| 16980 | 卡皮巴拉大炮发射炮弹 | - | 1 | shadows.png |
| 16986 | 毒水池 | model/C1/L4/Model/l4_04_01/sm_l4_gsgc_shuichi.fbx | 1 | t_l4_gsgc_shuichi.png |
| 17001 | 大日晷 | model/sprite3d/sm_l5_darigui.FBX | 1 | t_l5_rigui_darigui.png |
| 17002 | 小日晷 | model/sprite3d/sm_l5_xiaorigui.FBX | 1 | t_l5_rigui_xiaorigui.png |
| 17003 | 古代瓦罐 | model/sprite3d/sm_l5_gudaiwaguan.FBX | 1 | t_l5_gudaiwaguan.png |
| 17004 | 火晶 | model/sprite3d/sm_l4_suibing_03.FBX | 1 | t_l5_suibing_hong.png |
| 17005 | 将军令牌 | model/sprite3d/sm_l5_jiangjunlingpai.FBX | 1 | t_l5_jiangjunlingpai.png |
| 17006 | 锦囊道具 | model/sprite3d/sm_l5_jinnangdaoju.FBX | 1 | t_l5_jinnangdaoju.png |
| 17007 | 木咋特鸟蛋1 | model/sprite3d/sm_l5_daoju_dan_01.fbx | 1 | t_l5_daoju_dan_01.png |
| 17008 | 木咋特鸟蛋2 | model/sprite3d/sm_l5_daoju_dan_02.fbx | 1 | t_l5_daoju_dan_02.png |
| 17010 | 峡谷关大门 | model/sprite3d/sm_l5_xiagu_damen.FBX | 2 | t_l5_xiagu_damen_xiangjiaoshu.png, t_l5_xiagu_damen_men.png |
| 17014 | 进化芯片大 | model/sprite3d/sm_l4_jinhuaxinpian.fbx | 2 | t_l4_jinhuaxinpian_pingmu.png, t_l4_jinhuaxinpian.png |
| 17075 | 雨伞架 3把 | model/sprite3d/sm_l5_yusanjia_01.FBX | 1 | t_l5_yusanjia.png |
| 17260 | 泥便便 | model/sprite3d/sm_l5_bianbian.FBX | 1 | t_l5_bianbian.png |
| 17261 | 黄牛泥塑像 | model/sprite3d/sm_l5_huangniudiaoxiang.FBX | 1 | t_l5_huangniudiaoxiang.png |
| 17263 | 星座壁画 虎 | model/sprite3d/sm_l4_xingzuobihua_hu.fbx | 1 | t_l4_xingzuobihua_hu.png |
| 17264 | 星座壁画 鹊 | model/sprite3d/sm_l4_xingzuobihua_que.fbx | 1 | t_l4_xingzuobihua_que.png |
| 17268 | 飞鸽传书 | model/sprite3d/sm_l6_feigechuanshu_02.fbx | 1 | t_l6_feigechuanshu.png |
| 17269 | 飞鸽传书02 | model/sprite3d/sm_l6_feigechuanshu_01.fbx | 1 | t_l6_feigechuanshu.png |
| 17280 | 五色宝石 粉宝石 | model/sprite3d/sm_l6_baoshi_fen.fbx | 1 | t_l6_baoshi_fen.png |
| 17281 | 五色宝石 黄宝石 | model/sprite3d/sm_l6_baoshi_huang.fbx | 1 | t_l6_baoshi_huang.png |
| 17282 | 五色宝石 蓝宝石 | model/sprite3d/sm_l6_baoshi_lan.fbx | 1 | t_l6_baoshi_lan.png |
| 17283 | 五色宝石 绿宝石 | model/sprite3d/sm_l6_baoshi_lv.fbx | 1 | t_l6_baoshi_lv.png |
| 17284 | 五色宝石 紫宝石 | model/sprite3d/sm_l6_baoshi_zi.fbx | 1 | t_l6_baoshi_zi.png |
| 17285 | 橙子兵法 | model/sprite3d/sm_l6_chengzibinfa.fbx | 1 | t_l6_daoju_01.png |
| 17292 | 被打断消失飞箭 | model/sprite3d/sm_l5_feijian_daduan.FBX | 1 | t_l5_feijian_daduan.png |
| 17293 | 被打断消失箭雨 | model/sprite3d/sm_l5_jianyu_daduan.FBX | 1 | t_l5_feijian_daduan.png |
| 17391 | 飞箭 | model/sprite3d/sm_l5_feijian.FBX | 1 | t_l5_feijian.png |
| 17392 | 箭雨 | model/sprite3d/sm_l5_jianyu.FBX | 1 | t_l5_feijian.png |
| 17393 | 一堆黄金香蕉 | model/sprite3d/sm_l5_yiduihuangjinxiangjiao.FBX | 1 | t_l5_yiduihuangjingxiangjiao.png |
| 17394 | 一根黄金香蕉 | model/sprite3d/sm_l5_yigenhuangjinxiangjiao.FBX | 1 | t_l5_yiduihuangjingxiangjiao.png |
| 17395 | 锦囊 | model/sprite3d/sm_l5_jinnang.FBX | 1 | t_L5_jinnang.png |
| 17398 | 牢笼 | model/sprite3d/sm_l2_laolong.fbx | 1 | t_l2_laolong.png |
| 17560 | 雨伞架 2把 | model/sprite3d/sm_l5_yusanjia.fbx | 1 | t_l5_yusanjia.png |
| 17564 | 燃烧的火晶 | model/sprite3d/sm_l4_suibing_03.FBX | 1 | t_l5_suibing_hong.png |
| 17567 | 喵朝军营帐篷完整 | model/C1/L5/Model/l5_04_01/sm_l5_hdzk_jianzhu_02.FBX | 1 | t_l5_hdzk_jianzhu_mao.png |
| 17568 | 待机时空之眼 | model/sprite3d/sm_l5_shikongzhiyan.FBX | 1 | t_l5_shikongzhiyan.png |
| 17569 | 损坏侧翻卡皮巴拉大炮 | model/sprite3d/sm_l5_kapibaladapao.FBX | 1 | t_l5_kapibaladapao_2.png |
| 17570 | 待机卡皮巴拉大炮 | model/sprite3d/sm_l5_kapibaladapao.FBX | 1 | t_l5_kapibaladapao_1.png |
| 17571 | 卡皮巴拉军营帐篷 | model/C1/L5/Model/l5_04_01/sm_l5_hdzk_jianzhu_02.FBX | 1 | t_l5_hdzk_jianzhu_02_po.png |
| 17572 | 被轰炸卡皮巴拉军营帐篷 | model/sprite3d/sm_l5_hdzk_jianzhu_03_po.FBX | 1 | t_l5_hdzk_jianzhu_02_po.png |
| 17573 | 发光大日晷 | model/sprite3d/sm_l5_darigui.FBX | 1 | t_l5_rigui_darigui.png |
| 17574 | 发光小日晷 | model/sprite3d/sm_l5_xiaorigui.FBX | 1 | t_l5_rigui_xiaorigui.png |
| 17576 | 胡萝卜 | model/C1/L4/Model/l4_04_01/sm_l4_hulubo.fbx | 1 | t_l5_jwhuluobo.png |
| 17577 | 待机大蒸汽战舰 | model/C1/L5/Model/l5_03_01/sm_l5_kpbl_zhanchuan_01.FBX | 2 | t_l5_kpbl_zhanchuan_01_a.png, t_l5_kpbl_zhanchuan_01_b.png |
| 17578 | 小蒸汽战舰 | - | 2 | t_l5_weicheng_xiaochuan_02.png, t_l5_weicheng_xiaochuan_01.png |
| 17579 | 待机浮光鲤 | model/sprite3d/sm_l5_fuguangli.FBX | 1 | t_l5_fuguangli_D.png |
| 17758 | 时空之石 | model/sprite3d/sm_L5_shikongzhishi.FBX | 1 | t_L5_shikongzhishi_D.png |
| 17955 | 关闭待机武器箱 | model/sprite3d/sm_l5_xiangzi_01.FBX | 1 | t_l5_xiangrikui.png |
| 17956 | 持续出现电流武器箱 | model/sprite3d/sm_l5_xiangzi_01.FBX | 1 | t_l5_xiangrikui.png |
| 17957 | 睡莲 | model/sprite3d/sm_l6_jinglingshuilian.FBX | 1 | t_l6_jinglingshuilian.png |
| 17958 | 痒痒蒲公英 | model/sprite3d/sm_l6_yangyangpugongying.FBX | 1 | t_l6_yangyangpugongying.png |
| 17959 | 晕晕向日葵 | model/sprite3d/sm_l6_yunyunxiangrikui.FBX | 1 | t_l6_yunyunxiangrikui.png |
| 17960 | 寒冰蓝玫瑰 | model/sprite3d/sm_l6_hanbinglanmeigui.FBX | 1 | t_l6_hanbinglanmeigui.png |
| 17961 | BMI计算器 | model/sprite3d/sm_L6_BMIjisuanqi.FBX | 1 | t_L6_BMIjisuanqi_01.png |
| 17962 | 普通打印机 | model/sprite3d/sm_L6_putondayinji.FBX | 1 | t_L6_putondayinji.png |
| 17963 | 奢侈品打印机 | model/sprite3d/sm_L6_shechipindayinji.FBX | 1 | t_L6_shechipindayinji.png |
| 17964 | 自动播种机 | model/sprite3d/sm_L6_zidongbozhongji.FBX | 1 | t_L6_zidongbozhongji.png |
| 17983 | 好大的芝麻 | model/sprite3d/sm_l6_zhima_01.FBX | 1 | t_l6_juan.png |
| 17984 | 心想事橙（大） | model/sprite3d/sm_l6_chengzi_01.FBX | 1 | t_l6_juan.png |
| 17985 | 心想事橙（小） | model/sprite3d/sm_l6_chengzi_02.FBX | 1 | t_l6_juan.png |
| 17987 | 打开的峡谷关大门 | model/sprite3d/sm_l5_xiagu_damen.FBX | 2 | t_l5_xiagu_damen_xiangjiaoshu.png, t_l5_xiagu_damen_men.png |
| 17988 | 皇族套装 | model/sprite3d/sm_l6_huangzutaozhuang.FBX | 1 | t_l6_huangzutaozhuang.png |
| 17989 | 小乌云 | model/player/C_L6/yun/sm_l6_wuyun.fbx | 1 | t_l6_wuyun.png |
| 17990 | 检测狗 | - | 1 | shadows.png |
| 18001 | 空白金蛋 | model/sprite3d/sm_l6_dan_10.FBX | 2 | t_l6_dan_01.png, t_l6_juan.png |
| 18009 | 砸开金蛋空白 | model/sprite3d/sm_l6_dan_posun_10.FBX | 2 | t_l6_dan_01.png, t_l6_juan.png |
| 18010 | 砸金蛋锤 | model/sprite3d/sm_l6_zadanchuizi.FBX | 1 | t_l6_daoju_01.png |
| 18011 | 金鸡兽宝箱 | model/sprite3d/sm_l6_baoxiang.FBX | 2 | t_l6_juan.png, t_l6_baoxiang.png |
| 18012 | 豪宅券 | model/sprite3d/sm_l6_juan_02.FBX | 1 | t_l6_juan.png |
| 18013 | 免费御膳券 | model/sprite3d/sm_l6_juan_01.FBX | 1 | t_l6_juan.png |
| 18014 | 天穹仪 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi_01@skin.FBX | 1 | t_l6_tianqiongyi.png |
| 18016 | 新版天穹仪 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi_03@skin.FBX | 1 | t_l6_tianqiongyi.png |
| 18017 | 盖世英雄金锅锅 | model/sprite3d/sm_l6_tianqiongyi_04.FBX | 1 | t_l6_tianqiongyi.png |
| 18018 | 白菜仙人掌激光 | model/sprite3d/sm_l6_baicaixianrenzhangjiguang.FBX | 1 | t_l6_baicaixianrenzhangjiguang.png |
| 18019 | 蘑菇土豆天使炮 | model/sprite3d/sm_l6_mogutudoutianshipao.FBX | 1 | t_l6_mogutudoutianshipao.png |
| 18021 | 菠萝西瓜脉冲弹 | model/sprite3d/sm_l6_boluoxiguamaichongdan.FBX | 1 | t_l6_boluoxiguamaichongdan.png |
| 18128 | 蜡烛 | model/sprite3d/sm_kejianbuji_lazhu.fbx | 1 | t_kejianbuji_xiaowujian.png |
| 18129 | 宝箱 | model/sprite3d/sm_kejianbuji_baoxiang.fbx | 1 | t_kejianbuji_xiaowujian.png |
| 18130 | 九婴碎片 | model/sprite3d/sm_l1_jiuyinsuipian.fbx | 1 | t_l1_jyhn.png |
| 18131 | 《刺客机关屋观光手册》 | model/sprite3d/sm_l2_cikeguanguangshouce.fbx | 1 | t_l2_daoju.png |
| 18132 | 门上的锁 | model/sprite3d/sm_l2_menshangdesuo.fbx | 1 | t_l2_daoju.png |
| 18133 | 龙王茶壶 | model/sprite3d/sm_l2_longwangchahu.fbx | 1 | t_l2_daoju.png |
| 18358 | 土 | model/sprite3d/sm_l6_zhiwushitou_01.fbx | 1 | t_l6_zhiwushitou_01.png |
| 18359 | 凹凸曼西瓜 | model/sprite3d/sm_l6_xigua.fbx | 1 | t_l6_boluoxiguamaichongdan.png |
| 18360 | 天使蘑菇 | model/sprite3d/sm_l6_mogu.fbx | 1 | t_l6_mogu.png |
| 18361 | 超级菠萝 | model/sprite3d/sm_l6_boluo.fbx | 2 | t_l6_boluo_01.png, t_l6_boluoxiguamaichongdan.png |
| 18362 | 傲娇白菜 | model/sprite3d/sm_l6_dabaicai_01.fbx | 1 | t_l6_dabaicai_01.png |
| 18363 | 拽酷仙人掌 | model/sprite3d/sm_l6_xianrenzhang_01.fbx | 2 | t_l6_baicaixianrenzhangjiguang.png, t_l6_xianrenzhang_01.png |
| 18525 | 检测结果出现代码 | model/sprite3d/sm_l6_jiancejieguo.fbx | 1 | t_l6_jiancejieguo.png |
| 18530 | 天穹仪破碎版 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi_02@skin.FBX | 1 | t_l6_tianqiongyi.png |
| 18531 | 嘟嘟车+卡皮巴拉司机 | - | 1 | shadows.png |
| 18532 | 嘟嘟车+乘客 | - | 1 | shadows.png |
| 18646 | 食人花 | - | 1 | shadows.png |
| 18647 | 蒸汽破空 | - | 1 | shadows.png |
| 18652 | 坦克 | - | 1 | shadows.png |
| 18658 | 大乌云 | model/sprite3d/sm_l6_wuyun_02.fbx | 1 | t_l6_wuyun.png |
| 18659 | 祈雨大炮 | model/sprite3d/sm_L3_qiyudapao.fbx | 1 | t_L3_qiyudapao.png |
| 19352 | 定水神针 | model/sprite3d/sm_kejianbuji_jingubang.fbx | 1 | t_kejianbuji_jingubang.png |
| 19354 | 黑色大山 | model/sprite3d/sm_cg_heisedashan.fbx | 1 | t_cg_heisedashan.png |
| 19851 | 全向车 | - | 1 | shadows.png |
| 19857 | 牛车（破损版） | model/sprite3d/sm_cg_mache_01.fbx | 1 | t_cg_mache_01.png |
| 19858 | 牛车 | model/sprite3d/sm_cg_mache_02.FBX | 1 | t_cg_mache_02.png |
| 20167 | 黑色直线 | model/sprite3d/sm_zhixianheixian.FBX | 1 | - |
| 20168 | 转弯黑线 | model/sprite3d/sm_zhuanwanheixian.FBX | 1 | - |
| 20169 | 重点区域 | model/sprite3d/sm_zhongdianquyu.FBX | 1 | - |
| 20170 | 积雪 | model/C1/L3/Model/L3_04_02/sm_l4_xuekuai_01.fbx | 1 | t_l4_xuesong_01.png |
| 20172 | 大冰块 | model/sprite3d/sm_yj_dabingkuai.fbx | 1 | t_yj_dabingkuai.png |
| 20709 | 全向车_外卖 | model/sprite3d/sm_yj_huangniuwaimai.fbx | 2 | shadows.png, t_yj_huangniuwaimai.png |
| 20739 | 打人柳树枝 | model/sprite3d/sm_l7_daoju_liuzhi.fbx | 1 | t_l7_daoju_liuzhi.png |
| 20740 | 金币 | model/sprite3d/sm_l7_daoju_jinbi.fbx | 1 | t_l7_daoju_jinbi.png |
| 20758 | 传奇法袍 | model/sprite3d/sm_L7_chuanqifapao.fbx | 1 | t_l7_duizhangmofapao_yifu_D.png |
| 20761 | 小木牌 | model/sprite3d/sm_l7_daoju_mupai.fbx | 1 | t_l7_daoju_mupai.png |
| 20762 | 十八般厨艺箱 | model/sprite3d/sm_l7_daoju_chuyixiang.fbx | 1 | t_l7_daoju_chuyixiang.png |
| 20763 | 卷子 | model/sprite3d/sm_l7_daoju_shijuan.fbx | 1 | t_l7_daoju_shijuan.png |
| 20767 | 魔药桌 | model/C1/L7/Model/l7-04-01/sm_l7_yingdi_shiyanzhuo.FBX | 1 | t_l7_yingdi_shiyanzhuo.png |
| 20768 | 保安树种子 | model/sprite3d/sm_l7_daoju_zhongzi.fbx | 1 | t_l7_daoju_01.png |
| 20771 | 魔法异闻录 | model/sprite3d/sm_L7_mofayiwenlu.FBX | 1 | t_L7_mofayiwenlu_d.png |
| 20774 | 录取通知书 | model/sprite3d/sm_l7_dj_tongzhishu.fbx | 1 | t_l7_daoju_tongzhishu.png |
| 20775 | 杯子 | model/sprite3d/sm_l7_daoju_shuibei.fbx | 1 | t_l7_datietai.png |
| 20776 | 打铁台 | model/sprite3d/sm_l7_daoju_datietai.fbx | 1 | t_l7_datietai.png |
| 20777 | 铜钳锅 | model/C1/L7/Model/l7-03-01/sm_l7_myyws_pen01.FBX | 1 | t_l7_myyws_pen01.png |
| 20797 | 打人柳嘴炮1 | model/sprite3d/sm_l7_dj_zuipao_01.fbx | 1 | t_l7_daoju_zuipao.png |
| 20798 | 打人柳嘴炮2 | model/sprite3d/sm_l7_dj_zuipao_02.fbx | 1 | t_l7_daoju_zuipao.png |
| 20814 | 回响光谱01 | model/sprite3d/sm_l7_huixiangguangpu_01.FBX | 2 | t_l7_huixiangguangpu_02.png, t_l7_huixiangguangpu_01.png |
| 20815 | 回响光谱02 | model/sprite3d/sm_l7_huixiangguangpu_02.FBX | 2 | t_l7_huixiangguangpu_02.png, t_l7_huixiangguangpu_01.png |
| 20816 | 回响光谱03 | model/sprite3d/sm_l7_huixiangguangpu_03.FBX | 2 | t_l7_huixiangguangpu_02.png, t_l7_huixiangguangpu_01.png |
| 20817 | 回响光谱04 | model/sprite3d/sm_l7_huixiangguangpu_04.FBX | 2 | t_l7_huixiangguangpu_02.png, t_l7_huixiangguangpu_01.png |
| 20818 | 回响光谱05 | model/sprite3d/sm_l7_huixiangguangpu_05.FBX | 2 | t_l7_huixiangguangpu_02.png, t_l7_huixiangguangpu_01.png |
| 20819 | 回响光谱06 | model/sprite3d/sm_l7_huixiangguangpu_06.FBX | 1 | t_l7_huixiangguangpu_01.png |
| 20821 | 石中杖底石 | model/sprite3d/sm_l7_shizhongzhangdishi.FBX | 1 | t_l7_shizhongzhangdishi_D.png |
| 20822 | 乾坤袋 | model/sprite3d/sm_l7_daoju_qiankundai.fbx | 1 | t_l7_daoju_01.png |
| 20823 | 魔镜 | model/sprite3d/sm_l7_daoju_mojing.fbx | 1 | t_l7_daoju_mojing.png |
| 20824 | 魔法马车 | model/sprite3d/sm_l7_mofamache.FBX | 1 | t_l7_mofamache.png |
| 20825 | 关闭魔法宝箱 | model/sprite3d/sm_l7_mofabaoxiang.fbx | 1 | t_l7_mofabaoxiang.png |
| 20826 | 飞天扫帚 | model/sprite3d/sm_l7_feitiansaozhou.FBX | 1 | t_l7_feitiansaozhou_D.png |
| 20827 | 飞天扫帚（队长） | model/sprite3d/sm_l7_feitiansaozhou_duizhang.FBX | 1 | t_l7_feitiansaozhou_duizhang_D.png |
| 20828 | 飞天扫帚（百灵） | model/sprite3d/sm_l7_feitiansaozhou_bailing.FBX | 1 | t_l7_feitiansaozhou_bailing_D.png |
| 20829 | 飞剑 | model/sprite3d/sm_L7_feijian.FBX | 1 | t_L7_feijian_D.png |
| 20830 | 打开魔法宝箱 | model/sprite3d/sm_l7_mofabaoxiang.fbx | 1 | t_l7_mofabaoxiang.png |
| 20831 | 传奇魔杖 | model/sprite3d/sm_L7_chuanqimozhang.FBX | 1 | t_l7_chuanqimozhang_D.png |
| 20832 | 果立成果实 | model/sprite3d/sm_l7_guolicheng.FBX | 1 | t_l7_guolicheng.png |
| 20834 | 痒痒种子枪 | model/sprite3d/sm_L7_yangyangzhongziqiang.FBX | 2 | t_L7_yangyangzhongziqiang.png |
| 20835 | 藏宝图 | model/sprite3d/sm_l7_daoju_cangbaotu.fbx | 1 | t_l7_daoju_cangbaotu.png |
| 20837 | 普通法袍 | model/sprite3d/sm_l7_putongfapao.fbx | 1 | t_l7_putongfapao_D.png |
| 20838 | 美食摊 | model/sprite3d/sm_l7_baozi_01.FBX | 1 | t_l3_baozipu.png |
| 20841 | 时间之匙（完整） | model/sprite3d/sm_l7_yaoshi_01.FBX | 1 | t_l7_yaoshi_01.png |
| 20842 | 时间之匙碎片01 | model/sprite3d/sm_l7_yaoshisuipian_01.FBX | 1 | t_l7_yaoshi_01.png |
| 20843 | 时间之匙碎片02 | model/sprite3d/sm_l7_yaoshisuipian_02.FBX | 1 | t_l7_yaoshi_01.png |
| 20844 | 时间之匙碎片03 | model/sprite3d/sm_l7_yaoshisuipian_03.FBX | 1 | t_l7_yaoshi_01.png |
| 20845 | 时间之匙碎片04 | model/sprite3d/sm_l7_yaoshisuipian_04.FBX | 1 | t_l7_yaoshi_01.png |
| 20846 | 时间之匙碎片05 | model/sprite3d/sm_l7_yaoshisuipian_05.FBX | 1 | t_l7_yaoshi_01.png |
| 20847 | 时间之匙碎片06 | model/sprite3d/sm_l7_yaoshisuipian_06.FBX | 1 | t_l7_yaoshi_01.png |
| 20870 | 保安树01 | - | 1 | shadows.png |
| 20871 | 保安树02 | - | 1 | shadows.png |
| 20872 | 保安树03 | - | 1 | shadows.png |
| 20921 | 魔法三色灯 | model/sprite3d/sm_l7_daoju_sansedeng_02.fbx | 1 | t_l7_daoju_sansedeng.png |
| 20922 | 魔女包浆钳锅 | model/sprite3d/sm_l7_daoju_guanzi.FBX | 1 | t_l7_daoju_guanzi.png |
| 20925 | 毒刺 | model/sprite3d/sm_l7_duci.FBX | 1 | t_l7_duci.png |
| 20926 | 锤子 | model/sprite3d/sm_l7_dj_chuizi.fbx | 1 | t_L7_chutouchuizi.png |
| 20927 | 锄头 | model/sprite3d/sm_l7_dj_chutou.fbx | 1 | t_L7_chutouchuizi.png |
| 20928 | 天才笔记 | model/sprite3d/sm_L7_tiancaibiji.FBX | 1 | t_L7_tiancaibiji.png |
| 20929 | 百灵记忆球 | model/sprite3d/sm_l7_bailingjiyiqiu.FBX | 1 | t_l7_bailingjiyiqiu.png |
| 20930 | 炼金器材（桃子用） | model/sprite3d/sm_L7_lianyaodaoju.FBX | 1 | t_L7_lianyaodaoju.png |
| 21035 | 魔法三色灯亮红灯 | model/sprite3d/sm_l7_daoju_sansedeng_02.fbx | 1 | t_l7_daoju_sansedeng.png |
| 21036 | 魔法三色灯亮黄灯 | model/sprite3d/sm_l7_daoju_sansedeng_02.fbx | 1 | t_l7_daoju_sansedeng.png |
| 21037 | 魔法三色灯亮绿灯 | model/sprite3d/sm_l7_daoju_sansedeng_02.fbx | 1 | t_l7_daoju_sansedeng.png |
| 21038 | 普通魔镜 | model/sprite3d/sm_l7_daoju_mojing_02.fbx | 1 | t_l7_daoju_01.png |
| 21166 | 营地-小木屋 | model/C1/L7/Model/l7-04-01/sm_l7_yingdi_fangzi_01.FBX | 2 | t_l7_yingdi_fangzi_01_b.png, t_l7_yingdi_fangzi_01_a.png |
| 21259 | 花间露藤蔓 | model/player/C_L7/changraotengman/L7_huajianluyounian.FBX | 1 | L7_chanraotengwan_D.png |
| 21281 | 巨大荷花 | - | 1 | shadows.png |
| 21286 | 运输路线-运送目的地 | model/sprite3d/sm_l8_yunsumudidi.fbx | 1 | - |
| 21287 | 运输路线-货物装车点 | model/sprite3d/sm_l8_huowuzhuangchedian.fbx | 1 | - |
| 21288 | 运输路线-绿色方块区域 | model/sprite3d/sm_l8_yunsuluxianfangkuai.fbx | 1 | - |
| 21289 | 运输路线-棕色方块区域 | model/sprite3d/sm_l8_yunsuluxianfangkuai.fbx | 1 | - |
| 21301 | 自动行驶路线图 | model/sprite3d/sm_l8_luxiantu.fbx | 1 | t_l8_luxiantu01.png |
| 21302 | 取货送货路线图 | model/sprite3d/sm_l8_luxiantu.fbx | 1 | t_l8_luxiantu02.png |
| 21305 | 黑将 | model/sprite3d/sm_L8_jiang.FBX | 1 | t_L8_heijiang.png |
| 21306 | 黑士 | model/sprite3d/sm_L8_shi.FBX | 1 | t_L8_heishi.png |
| 21307 | 黑卒 | model/sprite3d/sm_L8_bing.FBX | 1 | t_L8_heizu.png |
| 21308 | 黑车 | model/sprite3d/sm_L8_che.FBX | 1 | t_L8_heiche.png |
| 21309 | 红炮 | model/sprite3d/sm_L8_pao.FBX | 1 | t_L8_hongpao.png |
| 21310 | 红车 | model/sprite3d/sm_L8_che.FBX | 1 | t_L8_hongche.png |
| 21311 | 红兵 | model/sprite3d/sm_L8_bing.FBX | 1 | t_L8_hongbing.png |
| 21312 | 红帅 | model/sprite3d/sm_L8_jiang.FBX | 1 | t_L8_hongshuai.png |
| 21313 | 马撕客旗子 | model/sprite3d/sm_l8_dj_mskqz.FBX | 1 | t_l8_dj_mskqz.png |
| 21314 | 激励马人横幅 | model/sprite3d/sm_l8_dj_hengfu.FBX | 1 | t_l8_dj_mskqz.png |
| 21315 | 红仕 | model/sprite3d/sm_L8_shi.FBX | 1 | t_L8_hongshi.png |
| 21316 | 黑砲 | model/sprite3d/sm_L8_pao.FBX | 1 | t_L8_heipao.png |
| 21317 | 装魔药的坩埚 | model/player/C_L7/zhinengxiaoche/sm_l8_daoju_myqg.FBX | 1 | t_l8_daoju_myqg.png |
| 21318 | 花瓣账单 | model/sprite3d/sm_l8_daoju_huaban.FBX | 1 | t_l8_daoju_huaban.png |
| 21319 | 喇叭 | model/sprite3d/sm_L8_laba.FBX | 1 | t_L8_laba.png |
| 21320 | 不一定唤龙笛 | model/sprite3d/sm_l8_longdi.fbx | 1 | t_l8_dj_longdi.png |
| 21323 | 保安树苗 | model/sprite3d/sm_l7_baoanshumiao.FBX | 1 | t_l7_baoanshumiao.png |
| 21324 | 一张画 | model/sprite3d/sm_L8_yizhanghua.fbx | 1 | t_L8_yizhanghua.png |
| 21387 | 魔法隔离屋 | model/sprite3d/sm_l8_geliwu_01.fbx | 4 | t_l8_hongwa_02.png, t_l8_geliwu_01_a.png, t_l8_hongwa_01.png, t_l8_geliwu_01_b.png |
| 21388 | 打字机 | model/sprite3d/sm_l9_dj_daziji.fbx | 1 | t_l9_dj_daziji.png |
| 21389 | 借阅记录 | model/sprite3d/sm_l9_dj_jyjl.fbx | 1 | t_l9_dj_01.png |
| 21392 | 神笔造墨锦囊 | model/sprite3d/sm_l9_dj_zmjn.FBX | 1 | t_l9_dj_zhituan.png |
| 21393 | 隐形兽尾毛 | model/sprite3d/sm_l9_dj_weimao.fbx | 1 | t_l9_dj_01.png |
| 21394 | 纸团 | model/sprite3d/sm_l9_dj_zhituan.FBX | 1 | t_l9_dj_zhituan.png |
| 21395 | 空的脑机接口 | model/C1/L8/Model/l8-01-01/sm_l8_daoju_pbj.FBX | 3 | t_l8_daoju_pbj_01.png, t_l8_daoju_pbj_02.png, t_l8_daoju_pbj_03.png |
| 21399 | 龙蛋 | model/sprite3d/sm_L8_longdan.fbx | 1 | t_L8_longdan_D.png |
| 21406 | 智能小车+厨艺箱 | - | 1 | shadows.png |
| 21407 | 智能小车+魔法坩埚 | - | 1 | shadows.png |
| 21548 | 路线 | model/sprite3d/sm_l8_luxian.fbx | 1 | - |
| 21574 | 龙宝宝3D精灵 | - | 1 | shadows.png |
| 21581 | 魔植白术 | model/sprite3d/sm_l8_daoju_baishu.FBX | 1 | t_l8_daoju_fuling.png |
| 21582 | 魔植茯苓 | model/sprite3d/sm_l8_daoju_fuling.FBX | 1 | t_l8_daoju_fuling.png |
| 21583 | 龙蛋02 | model/sprite3d/sm_L8_longdan_02.fbx | 1 | t_L8_longdan_D.png |
| 21585 | 字母龙鳞a | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_a_D.png |
| 21586 | 字母龙鳞b | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_b_D.png |
| 21587 | 字母龙鳞c | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_c_D.png |
| 21588 | 字母龙鳞k | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_k_D.png |
| 21589 | 字母龙鳞m | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_m_D.png |
| 21590 | 字母龙鳞o | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_o_D.png |
| 21591 | 字母龙鳞z | model/sprite3d/sm_L8_zimulonglin.FBX | 1 | t_L8_zimulonglin_z_D.png |
| 21595 | 烤糊土层1 | model/sprite3d/sm_l8_caidi_01.FBX | 1 | t_l8_caidi.png |
| 21596 | 烤糊土层2 | model/sprite3d/sm_l8_caidi_02.FBX | 1 | t_l8_caidi.png |
| 21721 | 景王电脑 | model/sprite3d/sm_l9_dj_jwdn.fbx | 1 | t_l9_dj_jwdn.png |
| 21722 | 相框01 | model/sprite3d/sm_l8_mwnj_xk_01.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 21723 | 相框02 | model/sprite3d/sm_l8_mwnj_xk_02.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 21724 | 相框03 | model/sprite3d/sm_l8_mwnj_xk_03.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 21725 | 相框04 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 21726 | 相框05 | model/sprite3d/sm_l8_mwnj_xk_05.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 21727 | 相框06 | model/sprite3d/sm_l8_mwnj_xk_06.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 21728 | 相框07 | model/sprite3d/sm_l8_mwnj_xk_07.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21729 | 相框08 | model/sprite3d/sm_l8_mwnj_xk_08.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21730 | 相框09 | model/sprite3d/sm_l8_mwnj_xk_09.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_02.png |
| 21731 | 相框10 | model/sprite3d/sm_l8_mwnj_xk_10.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21732 | 相框11 | model/sprite3d/sm_l8_mwnj_xk_11.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_02.png |
| 21733 | 相框12 | model/sprite3d/sm_l8_mwnj_xk_12.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_02.png |
| 21734 | 相框13 | model/sprite3d/sm_l8_mwnj_xk_13.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21735 | 相框14 | model/sprite3d/sm_l8_mwnj_xk_14.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21736 | 相框15 | model/sprite3d/sm_l8_mwnj_xk_15.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21737 | 相框16 | model/sprite3d/sm_l8_mwnj_xk_16.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_02.png |
| 21738 | 相框17 | model/sprite3d/sm_l8_mwnj_xk_17.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21739 | 相框18 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21740 | 相框19 | model/sprite3d/sm_l8_mwnj_xk_19.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21741 | 相框20 | model/sprite3d/sm_l8_mwnj_xk_20.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21742 | 相框21 | model/sprite3d/sm_l8_mwnj_xk_21.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21743 | 相框22 | model/sprite3d/sm_l8_mwnj_xk_22.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21744 | 相框23 | model/sprite3d/sm_l8_mwnj_xk_23.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_02.png |
| 21745 | 相框24 | model/sprite3d/sm_l8_mwnj_xk_24.fbx | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_01.png |
| 21746 | 相框25 | model/sprite3d/sm_l8_mwnj_xk_25.FBX | 2 | t_l8_mwnj_xp_01.png, t_l8_mwnj_zpq_02.png |
| 21749 | 魔法坩埚 | model/sprite3d/sm_l8_daoju_myqg.FBX | 1 | t_l8_daoju_myqg_lv.png |
| 21753 | 智能小车魔药坩埚绿 | - | 1 | shadows.png |
| 21998 | 围栏爬藤_精灵版 | - | 1 | shadows.png |
| 21999 | 6张照片01 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_L8_daoju_xiangpian_01.png, t_l8_mwnj_zpq_01.png |
| 22000 | 6张照片02 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_L8_daoju_xiangpian_02.png, t_l8_mwnj_zpq_01.png |
| 22001 | 6张照片03 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_L8_daoju_xiangpian_03.png, t_l8_mwnj_zpq_01.png |
| 22117 | 6张照片04 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_L8_daoju_xiangpian_04.png, t_l8_mwnj_zpq_01.png |
| 22118 | 6张照片05 | model/sprite3d/sm_l8_mwnj_xk_11.fbx | 2 | t_L8_daoju_xiangpian_05.png, t_l8_mwnj_zpq_02.png |
| 22119 | 6张照片06 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_L8_daoju_xiangpian_06.png, t_l8_mwnj_zpq_01.png |
| 22120 | 装相片的箱子 | model/sprite3d/sm_l6_baoxiang.FBX | 1 | t_l6_baoxiang.png |
| 22126 | 宝藏堆 | model/sprite3d/sm_l6_baoxiang.FBX<br>model/sprite3d/sm_l7_mofabaoxiang.fbx | 2 | t_l7_mofabaoxiang.png, t_l6_juan.png |
| 22127 | 宝藏堆散开 | model/sprite3d/sm_l6_baoxiang.FBX<br>model/sprite3d/sm_l7_mofabaoxiang.fbx | 2 | t_l6_juan.png, t_l7_mofabaoxiang.png |
| 22131 | 桥板数字2 | model/sprite3d/sm_l9_banqiao_2.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22132 | 桥板数字5 | model/sprite3d/sm_l9_banqiao_5.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22133 | 桥板数字7 | model/sprite3d/sm_l9_banqiao_7.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22134 | 桥板数字9 | model/sprite3d/sm_l9_banqiao_9.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22135 | 桥板英文 i | model/sprite3d/sm_l9_banqiao_i.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22136 | 桥板英文k | model/sprite3d/sm_l9_banqiao_k.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22137 | 桥板英文n | model/sprite3d/sm_l9_banqiao_n.fbx | 2 | t_l4_xfzd_huojian.png, t_l9_banqiao_zimushuzi.png |
| 22139 | 运输路线-cg | model/sprite3d/sm_l4_yunsuluxian.fbx | 1 | - |
| 22140 | 营地-学生宿舍01 | model/sprite3d/sm_l8_xsss_01.FBX | 4 | shadows.png, t_l8_xsss_01.png, t_l8_xsss_02.png, t_l8_xueyuan_fxjz_fangzi_07.png |
| 22141 | 营地-学生宿舍02 | model/sprite3d/sm_l8_xsss_02.FBX | 5 | t_l8_xsss_03.png, t_l8_xsss_01.png, shadows.png, t_l8_xsss_02.png, t_l8_xueyuan_fxjz_fangzi_07.png |
| 22142 | 营地-学生宿舍03 | model/sprite3d/sm_l8_xsss_03.FBX | 5 | t_l8_xsss_03.png, t_l8_xsss_01.png, shadows.png, t_l8_xsss_02.png, t_l8_xueyuan_fxjz_fangzi_07.png |
| 22143 | 营地-学生宿舍04 | model/C1/L7/Model/l7-01-08/sm_l8_xueyuan_fxjz_fangzi_07.fbx | 4 | t_l8_ziwa_02.png, shadows.png, t_l8_ziwa_01.png, t_l8_xueyuan_fxjz_fangzi_07.png |
| 22149 | 焦黑痕迹 | - | 1 | t_l8_daoju_henji_01.png |
| 22160 | 兽栏-解锁后 | - | 1 | shadows.png |
| 22223 | 虚拟屏幕 | model/sprite3d/sm_L6_xunipingmu.FBX | 1 | t_L6_xunipingmu.png |
| 22224 | 打字机-坏掉 | model/sprite3d/sm_l9_dj_daziji_po.fbx | 1 | t_l9_dj_daziji_po.png |
| 22225 | 金苹果 | model/sprite3d/sm_l8_jinpinguo.FBX | 1 | t_l8_jinpinguo.png |
| 22226 | 奇异精灵草 | model/sprite3d/sm_l8_qiyijinglingcao.FBX | 1 | t_l8_qiyijinglingcao.png |
| 22227 | 自食奇果 | model/sprite3d/sm_l8_zishiqiguo.FBX | 1 | t_l8_zishiqiguo.png |
| 22228 | 借阅记录 | model/sprite3d/sm_L9_jieyuejilu.FBX | 1 | t_L9_jieyuejilu_d.png |
| 22229 | 《重生之我在喵朝当女帝》 | model/sprite3d/sm_L9_nvdihua.fbx | 1 | t_L9_nvdihua_d.jpg |
| 22230 | 欧阳日记本 | model/sprite3d/sm_L9_ouyangriji.FBX | 1 | t_L9_ouyangriji_D.png |
| 22232 | 打招呼的信鸽 | model/player/C_L9/xinge/L9_xinge@skin.FBX | 2 | L9_xinge_D.png, L9_xinge_yan_D.png |
| 22233 | 待机的信鸽 | model/player/C_L9/xinge/L9_xinge@skin.FBX | 2 | L9_xinge_D.png, L9_xinge_yan_D.png |
| 22235 | 穿梭秘籍咒-残片01 | model/sprite3d/sm_l9_chuansuozhou_01.fbx | 1 | t_l9_chuansuozhou.png |
| 22236 | 穿梭秘籍咒-残片02 | model/sprite3d/sm_l9_chuansuozhou_02.fbx | 1 | t_l9_chuansuozhou.png |
| 22237 | 穿梭秘籍咒-残片完 | model/sprite3d/sm_l9_chuansuozhou.fbx | 1 | t_l9_chuansuozhou.png |
| 22239 | 祈雨大炮_车轮 | - | 1 | shadows.png |
| 22240 | 飞行的信鸽 | model/player/C_L9/xinge/L9_xinge@skin.FBX | 2 | L9_xinge_D.png, L9_xinge_yan_D.png |
| 22241 | 树枝 | model/sprite3d/sm_cg_shuzhi.fbx | 1 | t_cg_shuzhi.png |
| 22242 | 浮空中转站 | model/sprite3d/sm_l9_dj_zzz.FBX | 3 | t_l9_dj_zzz_02.png, t_l9_dj_zzz_01.png, t_l8_hongwa_01.png |
| 22245 | 图书馆规则内页 | model/sprite3d/sm_l9_guizeneiye.fbx | 1 | t_l9_guizeneiye.png |
| 22246 | 椅子 | - | 1 | shadows.png |
| 22247 | 椅子01 | - | 1 | shadows.png |
| 22248 | 椅子02 | - | 1 | shadows.png |
| 22363 | 马撕客的火箭 | model/sprite3d/sm_l9_masikehuojian.FBX | 1 | t_l9_masikehuojian.png |
| 22364 | 马撕客的火箭坠落 | model/sprite3d/sm_l9_masikehuojian_zhuiluo.FBX | 1 | t_l9_masikehuojian.png |
| 22366 | 尖叫鸡 | model/sprite3d/sm_l9_jianjiaoji.FBX | 1 | t_l9_jianjiaoji.png |
| 22367 | 空魔药瓶 | model/sprite3d/sm_l9_dj_moyaoping_01.FBX | 1 | t_l9_dj_moyaoping.png |
| 22368 | 魔药瓶（装龙泪） | model/sprite3d/sm_l9_dj_moyaoping_02.FBX | 1 | t_l9_dj_moyaoping.png |
| 22369 | 会飞的书 | - | 1 | shadows.png |
| 22441 | 浮空魔法U | model/sprite3d/sm_l9_dj_mofazhuan_u.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22442 | 浮空魔法砖01 | model/sprite3d/sm_l9_dj_mofazhuan_01.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22443 | 浮空魔法砖02 | model/sprite3d/sm_l9_dj_mofazhuan_02.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22444 | 浮空魔法砖03 | model/sprite3d/sm_l9_dj_mofazhuan_03.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22445 | 浮空魔法砖04 | model/sprite3d/sm_l9_dj_mofazhuan_04.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22446 | 浮空魔法砖C | model/sprite3d/sm_l9_dj_mofazhuan_c.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22447 | 浮空魔法砖F | model/sprite3d/sm_l9_dj_mofazhuan_f.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22448 | 浮空魔法砖o | model/sprite3d/sm_l9_dj_mofazhuan_o.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22449 | 浮空魔法砖T | model/sprite3d/sm_l9_dj_mofazhuan_t.FBX | 1 | t_l9_dj_mofazhuan.png |
| 22579 | 被斩断的麻绳 | model/sprite3d/sm_l9_dj_masheng.FBX | 1 | t_l9_jianjiaoji.png |
| 22581 | 冰箭 | model/sprite3d/sm_l9_bingjian_01.FBX | 1 | t_l9_binghua.png |
| 22582 | 锻造材料堆金子 | model/sprite3d/sm_l9_dj_cailiaodui_02.FBX | 1 | t_l9_jianjiaoji.png |
| 22583 | 锻造材料堆木头 | model/sprite3d/sm_l9_dj_cailiaodui_01.FBX | 1 | t_l9_jianjiaoji.png |
| 22584 | 锻造材料堆石头 | model/sprite3d/sm_l9_dj_cailiaodui_04.FBX | 1 | t_l9_jianjiaoji.png |
| 22585 | 锻造材料堆铁矿 | model/sprite3d/sm_l9_dj_cailiaodui_03.FBX | 1 | t_l9_jianjiaoji.png |
| 22586 | 环湖马拉松奖杯 | model/sprite3d/sm_l9_jiangbei.FBX | 1 | t_l9_jiangbei.png |
| 22587 | 金色墨水 | model/sprite3d/sm_l9_jinsemoshui.FBX | 1 | t_l9_binghua.png |
| 22588 | 玉砚 | model/sprite3d/sm_l9_dj_yuyan.FBX | 1 | t_l9_dj_yuyan.png |
| 22589 | 玉墨 | model/sprite3d/sm_l9_dj_yumo.FBX | 1 | t_l9_dj_yuyan.png |
| 22590 | 漂浮 浮动的状态闪现花 | model/player/C_L9/shanxianhua/sm_L9_shanxianhua@skin.FBX | 2 | t_L9_shanxianhua_D.png, t_L9_shanxianhua_yan_D.png |
| 22591 | 营地升级-增加武器库 | model/C1/L7/Model/l7-04-01/sm_l7_yingdi_duanzao_01/sm_l7_yingdi_duanzao_01.FBX | 2 | t_l7_yingdi_duanzao_01_b.png, t_l7_yingdi_duanzao_01_a.png |
| 22592 | 信号弹红  烟花 | model/sprite3d/sm_l9_dj_xinhaodan_02.FBX | 1 | t_l9_jianjiaoji.png |
| 22593 | 信号弹蓝 | model/sprite3d/sm_l9_dj_xinhaodan_01.FBX | 1 | t_l9_jianjiaoji.png |
| 22594 | 乾坤神笔待机 | model/player/C_L9/qiankunshenbi/qiankunshenbi_01@skin.FBX | 1 | t_l9_dj_01.png |
| 22595 | 大炮 | model/sprite3d/sm_L9_qiyudapao_chelun.FBX | 1 | t_L9_qiyudapao_chelun_d.png |
| 22616 | 隐形兽住所 | model/sprite3d/sm_l9_yxszs.FBX | 2 | t_l9_yxszs02.png, t_l9_yxszs01.png |
| 22617 | 发光神笔造墨锦囊 | model/sprite3d/sm_l9_dj_zmjn.FBX | 1 | t_l9_dj_zhituan.png |
| 22618 | 强化玉砚 | model/sprite3d/sm_l9_dj_yuyan.FBX | 1 | t_l9_dj_yuyan.png |
| 22749 | 枯萎月光藤-幼苗 | model/sprite3d/sm_L9_yueguangteng_youmiaokuwei.FBX | 1 | t_L9_yueguangteng_youmiaokuwei_d.png |
| 22750 | 精灵画布 | model/sprite3d/sm_l9_dj_jlhb.FBX | 2 | t_l9_dj_jlhb.png, t_l9_dj_jlhb_jingling.png |
| 22751 | 2张高光照片01 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_l8_mwnj_zpq_01.png, t_L9_daoju_ggzp_01.png |
| 22752 | 2张高光照片02 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_l8_mwnj_zpq_01.png, t_L9_daoju_ggzp_02.png |
| 22753 | 不会动的画1 | model/sprite3d/sm_l9_xiangkuang_01.fbx | 2 | t_l9_hua_03.png, t_l8_mwnj_xk.png |
| 22754 | 不会动的画2 | model/sprite3d/sm_l9_xiangkuang_01.fbx | 2 | t_l9_hua_02.png, t_l8_mwnj_xk.png |
| 22755 | 不会动的画3 | model/sprite3d/sm_l9_xiangkuang_01.fbx | 2 | t_l9_hua_01.png, t_l8_mwnj_xk.png |
| 22756 | 画中人1待机 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 22757 | 画中人1说话 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 22758 | 画中人2wink | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 22759 | 画中人2待机 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 22760 | 画中人2说话 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 22761 | 月光藤-成熟（结果） | model/sprite3d/sm_L9_yueguangteng_chengshu.FBX | 1 | t_L9_yueguangteng_chengshu_d.png |
| 22762 | 月光藤果实 | model/sprite3d/sm_L9_yueguangteng_guoshi.FBX | 1 | t_L9_yueguangteng_guoshi_d.png |
| 22763 | 正常月光藤-幼苗 | model/sprite3d/sm_L9_yueguangteng_youmiao.FBX | 1 | t_L9_yueguangteng_youmiao_d.png |
| 22766 | 密码锁开锁 | model/sprite3d/sm_l9_jianlaodamen.fbx | 2 | t_l9_jiannao_03_caimao.png, t_l9_jiannao_04.png |
| 22771 | 密码锁待机 | model/sprite3d/sm_l9_jianlaodamen.fbx | 2 | t_l9_jiannao_04.png, t_l9_jiannao_03.png |
| 22772 | 监牢大门关闭 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX | 5 | t_l9_jiannao_04.png, t_l9_jiannao_01.png, t_l9_jiannao_03.png, t_l9_jiannao_05.png, t_l9_jiannao_09.png |
| 22773 | 监牢大门打开 | model/sprite3d/sm_l9_jianlaodamen.fbx | 5 | t_l9_jiannao_04.png, t_l9_jiannao_01.png, t_l9_jiannao_03.png, t_l9_jiannao_05.png, t_l9_jiannao_09.png |
| 22774 | 景王电脑蓝屏 | model/sprite3d/sm_l9_dj_jwdn.fbx | 1 | t_l9_dj_jwdn_lanping.png |
| 22780 | 高光照片9-1 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_l9_gaoguangzhaopian01.png, t_l8_mwnj_zpq_01.png |
| 22804 | 牛皮纸 | model/sprite3d/sm_l8_niupizhi.fbx | 1 | t_l8_niupizhi.png |
| 22805 | 高光照片9-2 | model/sprite3d/sm_l8_mwnj_xk_18.fbx | 2 | t_l8_mwnj_zpq_01.png, t_l9_gaoguangzhaopian02.png |
| 22889 | 《逆袭之龙傲天星途闪耀》 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 3 | t_L9_daoju_ggzp_03.png, t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 23261 | 母龙锁链 | model/player/C_L8/mulongsuolian/sm_l8_mulongsuolian.FBX | 1 | t_l8_mulongsuolian.png |
| 23263 | 《重生之xxxxxxx》01 | model/sprite3d/sm_l8_mwnj_xk_01.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 23264 | 《重生之xxxxxxx》02 | model/sprite3d/sm_l8_mwnj_xk_02.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 23265 | 《重生之xxxxxxx》03 | model/sprite3d/sm_l8_mwnj_xk_03.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 23266 | 《重生之xxxxxxx》04 | model/sprite3d/sm_l8_mwnj_xk_04.FBX | 2 | t_l8_mwnj_xp.png, t_l8_mwnj_xk.png |
| 23414 | 全向车_生命罗卜 | - | 1 | shadows.png |
| 23421 | 美食摊 | model/sprite3d/sm_yj_canche.FBX | 3 | t_yj_canche02.png, t_yj_canche01.png, t_yj_canche03.png |
| 23422 | 玩具摊 | model/sprite3d/sm_yj_wanjutan.FBX | 3 | t_yj_wanjutan_b.png, t_yj_wanjutan.png, t_yj_wanjutan_a.png |
| 23423 | 气球摊 | model/sprite3d/sm_yj_qiqiutan.FBX | 3 | t_yj_qiqiutan_02.png, t_yj_qiqiutan_01.png, t_yj_qiqiutan_03.png |
| 23547 | 保安树叶子 | model/sprite3d/sm_l9_baoanshuyezi.fbx | 1 | L7_baoanshu_02_shenti_D.png |
| 23548 | 一箱胡萝卜 | model/sprite3d/sm_L9_dj_muxiang_01.FBX | 2 | t_l4_huluobo.png, t_L9_dj_muxiang_a.png |
| 23549 | 热气球条幅 | model/sprite3d/sm_yj_reqiqiu.FBX | 1 | t_L9_dj_muxiang_a.png |
| 23577 | 小鱼干 | model/sprite3d/sm_l9_xiaoyugan.fbx | 1 | t_l9_xiaoyugan.png |
| 23749 | 小精灵_3D精灵版 | - | 1 | shadows.png |
| 23751 | 鹦鹉草叉_3D精灵版 | - | 1 | shadows.png |
| 23753 | 小熊猫马桶撅_3D精灵版 | - | 1 | shadows.png |
| 23754 | 冷不丁_3D精灵版 | - | 1 | shadows.png |
| 23794 | 卡皮巴拉士兵06_3D精灵版 | - | 1 | shadows.png |
| 23795 | 粉红河马_3D精灵版 | - | 1 | shadows.png |
| 23796 | 运输路线4-4 | model/sprite3d/sm_l8_yunsumudidi_4-4.fbx | 1 | - |
| 23797 | 土拨鼠长老红_3D精灵版 | - | 1 | shadows.png |
| 23798 | 土拨鼠长老绿_3D精灵版 | - | 1 | shadows.png |
| 23799 | 土拨鼠长老蓝_3D精灵版 | - | 1 | shadows.png |
| 23933 | 一车爆炸矿石 | model/sprite3d/sm_l10_ycks.FBX | 1 | t_l10_ycpg.png |
| 23934 | 舔狗魔镜 | model/sprite3d/sm_l10_jingzi.FBX | 1 | t_l10_jingzi.png |
| 23935 | 九转还魂丹 | model/sprite3d/sm_l10_jzhhd.FBX | 1 | t_l10_ycpg.png |
| 23936 | 通关文牒 | model/sprite3d/sm_l10_tgwd.FBX | 1 | t_l10_ycpg.png |
| 23937 | 引爆器 | model/sprite3d/sm_l10_ybq.FBX | 1 | t_l10_jingzi.png |
| 23938 | 一车苹果 | model/sprite3d/sm_l10_ycpg.FBX | 1 | t_l10_ycpg.png |
| 23939 | 意识碎片（蓝色） | model/sprite3d/sm_l10_yssp.FBX | 1 | t_l10_yssp.png |
| 23940 | 意识碎片（紫色） | model/sprite3d/sm_l10_yssp_01.FBX | 1 | t_l10_yssp_01.png |
| 23941 | 意识碎片（红色） | model/sprite3d/sm_l10_yssp_02.FBX | 1 | t_l10_yssp_02.png |
| 23942 | 种植指南小册子 | model/sprite3d/sm_l10_zhidaoshu.FBX | 1 | t_l10_jingzi.png |
| 23956 | 碎掉的意识碎片（红色） | model/sprite3d/sm_l10_yssp_02.FBX | 1 | t_l10_yssp_02_sui.png |
| 23957 | 碎掉的意识碎片（紫色） | model/sprite3d/sm_l10_yssp_01.FBX | 1 | t_l10_yssp_01_sui.png |
| 23958 | 碎掉的意识碎片（蓝色） | model/sprite3d/sm_l10_yssp.FBX | 1 | t_l10_yssp_sui.png |
| 23967 | 大礼帽3D精灵版 | - | 1 | shadows.png |
| 23977 | 朋友一生一起走锁 | model/sprite3d/sm_l10_suo.fbx | 1 | t_l10_suo.png |
| 24137 | 疯帽匠3D精灵版 | - | 1 | shadows.png |
| 24166 | 社牛水晶球 | model/sprite3d/sm_l10_sheniushuijingqiu.FBX | 1 | t_l10_sheniushuijingqiu.png |
| 24167 | 小铲子（道具） | model/sprite3d/sm_L10_chanzi.FBX | 1 | t_L10_chanzi.png |
| 24168 | 小锄头（道具） | model/sprite3d/sm_L10_chutou.FBX | 1 | t_L10_chutou.png |
| 24169 | 苹果花 | model/sprite3d/sm_l10_pingguohua.FBX | 1 | t_l10_pingguohua.png |
| 24171 | 银制匕首 | model/sprite3d/sm_l10_bishou.FBX | 1 | t_l10_bishou.png |
| 24172 | 行李 | model/sprite3d/sm_l10_xingli.FBX | 1 | t_l10_xingli.png |
| 24177 | 变大蛋糕 | model/sprite3d/sm_l10_bddg.FBX | 1 | - |
| 24178 | 好事坏事全看见魔法屏 | model/sprite3d/sm_l10_mfp.FBX | 1 | t_l10_mfp.png |
| 24179 | 205胶水（有求必应屋道具已更新） | model/sprite3d/sm_l10_jiaoshui.FBX | 1 | t_l10_jiaoshui.png |
| 24180 | 205胶水 | model/sprite3d/sm_l10_jiaoshui_02.fbx | 1 | t_l10_jiaoshui_02.png |
| 24181 | 玫瑰（半变化形态） | model/sprite3d/sm_l10_meigui_banbianhuaxingtai.FBX | 2 | t_l10_meigui_banbianhuaxingtai_biaoqing.png, t_l10_meigui_banbianhuaxingtai.png |
| 24182 | 狼毒草 | model/sprite3d/sm_l10_langducao.FBX | 1 | t_l10_langducao.png |
| 24190 | 蓝色茶壶 | model/sprite3d/sm_l10_chhcz_chahu04.fbx | 1 | t_l10_chhcz_lazhu.png |
| 24191 | 粉色茶壶 | model/sprite3d/sm_l10_chhcz_chahu01.fbx | 1 | t_l10_chhcz_chahu.png |
| 24192 | 棕色茶壶 | model/sprite3d/sm_l10_chhcz_chahu03.fbx | 1 | t_l10_chhcz_chahu.png |
| 24193 | 紫色茶壶 | model/sprite3d/sm_l10_chhcz_chahu02.fbx | 1 | t_l10_chhcz_chahu.png |
| 24194 | 黄色咖啡杯 | model/sprite3d/sm_l10_chhcz_chabei01.fbx | 1 | t_l10_chhcz_chabei_01.png |
| 24195 | 绿色咖啡杯 | model/sprite3d/sm_l10_chhcz_chabei02.fbx | 1 | t_l10_chhcz_chabei_02.png |
| 24207 | 喷洒装置 | model/sprite3d/sm_l10_pszz.FBX | 1 | t_l10_mfp.png |
| 24208 | 密码备忘录 | model/sprite3d/sm_l10_bwl.fbx | 1 | t_l10_bwl.png |
| 24649 | 蓝色地毯 | model/C1/L10/Model/l10-03-01/sm_l10_yscb_ditan_hong.fbx | 1 | t_l10_yscb_ditanlan.png |
| 24681 | 高光照片L10 | model/sprite3d/sm_l8_mwnj_xk_11.fbx | 2 | t_l10_gaoguangzhaopian01.png, t_l8_mwnj_zpq_02.png |
| 24683 | 龙鳞 | model/sprite3d/sm_L10_longlin.FBX | 1 | t_L10_longlin_D.png |
| 24684 | 一滩水 | model/sprite3d/sm_L10_yitanshui.fbx | 1 | t_sm_L10_yitanshui.png |
| 24685 | 驱狼铃 | model/sprite3d/sm_l10_qll.FBX | 1 | t_l10_qll.png |
| 24687 | 挣扎痕迹 | model/sprite3d/sm_L10_zhengzhahenji.fbx | 2 | t_l9_masikehuojian_zhuiluo.png, L10_masike_zhansun_shenti_D.png |
| 24700 | 陷阱（开） | model/sprite3d/sm_L10_xianjingkai.fbx | 1 | t_L10_jian.png |
| 25074 | 奖杯 | model/sprite3d/sm_l11_jiangbei.fbx | 1 | t_l11_jiangbei.png |
| 25085 | 钻石 | model/sprite3d/sm_l11_zuanshi.FBX | 1 | t_l11_zuanshi.png |
| 25086 | 碳粉 | model/sprite3d/sm_l11_tanfen.FBX | 1 | t_l11_tanfen.png |
| 25087 | 贝壳 | model/sprite3d/sm_l11_beike.FBX | 1 | t_l11_beike.png |
| 25088 | 珍珠 | model/sprite3d/sm_l11_zhenzhu.FBX | 1 | t_l11_beike.png |
| 25089 | 珍珠粉末 | model/sprite3d/sm_l11_zhenzhufen.FBX | 1 | t_l11_zhenzhufen.png |
| 25090 | 破镜重圆 | model/sprite3d/sm_l11_pjcy.FBX | 1 | t_l11_pjcy.png |
| 25091 | 脆脆红蛋 | model/sprite3d/sm_l11_hongdan.fbx | 1 | t_l11_hongdan.png |
| 25092 | 麦穗 | model/sprite3d/sm_l11_maisui.fbx | 1 | t_l11_maisui.png |
| 25093 | 旋转椅 | model/sprite3d/sm_l11_xzy_zhuanyi.FBX | 1 | t_l11_xzy_zhuanyi.png |
| 25095 | 金子 | model/sprite3d/sm_l11_jinzi.FBX | 1 | t_l11_daoju01_01.png |
| 25096 | 寻龙分金尺 | model/sprite3d/sm_l11_fenjinchi.FBX | 1 | t_l11_daoju01_02.png |
| 25097 | 魔法生化肥料 | model/sprite3d/sm_l11_huafei.FBX | 1 | t_l11_daoju01_01.png |
| 25111 | 森林之声 | model/sprite3d/sm_l11_slzs.FBX | 1 | t_l11_slzs.png |
| 25283 | 符咒 | model/sprite3d/sm_l11_fuzhou.FBX | 1 | t_l11_fuzhou.png |
| 25284 | 咒语残本 | model/sprite3d/sm_l11_zycb.FBX | 1 | t_l11_zycb.png |
| 25285 | 狼人被绑 | model/sprite3d/sm_L10_langren_shengzi.FBX | 1 | t_L10_langren_shengzi.png |
| 25286 | 长生果 小 | model/sprite3d/sm_l11_csg_01.FBX | 1 | t_l11_daoju01_02.png |
| 25287 | 长生果 中 | model/sprite3d/sm_l11_csg_02.FBX | 1 | t_l11_daoju01_02.png |
| 25288 | 长生果 大 | model/sprite3d/sm_l11_csg_03.FBX | 1 | t_l11_daoju01_02.png |
| 25425 | 灰烬（金子）地上 | model/sprite3d/sm_l11_huijingjingzi.fbx | 2 | t_l11_huijingjingzi.png, t_l11_huijingjingzi02.png |
| 25426 | 灰烬（金子)空中 | model/sprite3d/sm_l11_jinzi.FBX | 1 | t_l11_huijingjinzi03.png |
| 25442 | 千面神灯 | model/sprite3d/sm_l11_qmsd.FBX | 1 | t_l11_qmsd.png |
| 25450 | 好事坏事全看见魔法屏04 | - | 1 | t_quanpingmanhuahuiyi.png |
| 25463 | 地球仪 | model/C1/l9/Model/l9-01-01/sm_l9_tsg03_wj02.FBX | 1 | t_l9_tsg03_wjxk02.png |
| 25464 | 天平 | model/C1/L7/Model/l7-03-01/sm_l7_myyws_tianping.fbx | 1 | t_l7_myyws_tianping.png |
| 25465 | 烛台 | model/C1/l9/Model/l9-01-01/sm_l9_tsg03_wj01.FBX | 1 | t_l9_tsg03_wjxk02.png |
| 25466 | 魔法书 | model/C1/l9/Model/l9-01-01/sm_l9_tsg02_shu_01.fbx | 1 | t_l9_tsg02_shu.png |
| 25467 | 魔药瓶 | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_01.FBX | 1 | t_l7_myy_pingzi_01.png |
| 25522 | 楼梯指示牌 | model/C1/l9/Model/l9-01-01/sm_l9_tsg05_lupai.FBX | 1 | t_l9_dj_lupai.png |
| 25612 | 灰色桥板材料j | model/sprite3d/sm_l9_bancai_shi03.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25613 | 灰色桥板材料l | model/sprite3d/sm_l9_bancai_shi01.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25614 | 灰色桥板材料r | model/sprite3d/sm_l9_bancai_shi02.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25615 | 灰色桥板材料u | model/sprite3d/sm_l9_bancai_shi04.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25616 | 蓝色板桥材料a | model/sprite3d/sm_l9_bancai_bing01.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25617 | 蓝色板桥材料b | model/sprite3d/sm_l9_bancai_bing02.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25618 | 蓝色板桥材料m | model/sprite3d/sm_l9_bancai_bing03.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25619 | 蓝色板桥材料n | model/sprite3d/sm_l9_bancai_bing04.fbx | 2 | t_l9_bancai_02.png, t_l9_bancai_01.png |
| 25620 | 魔药瓶（红） | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_03.FBX | 1 | t_l7_myy_pingzi_02.png |
| 25621 | 魔药瓶（黄） | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_02.FBX | 1 | t_l7_myy_pingzi_01.png |
| 25622 | 魔药瓶（绿） | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_04.FBX | 1 | t_l7_myy_pingzi_01.png |
| 25623 | 魔药瓶（深蓝） | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_01.FBX | 1 | t_l7_myy_pingzi_02.png |
| 25625 | 魔药瓶（紫） | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_03.FBX | 1 | t_l7_myy_pingzi_01.png |
| 25626 | 坩锅（黑） | model/C1/L7/Model/l7-03-01/sm_l7_myyws_pen01.FBX | 1 | t_l7_myyws_pen01b.png |
| 25627 | 水晶碎片 | model/sprite3d/sm_l11_shuijingsuipian.FBX | 1 | t_l11_shuijingsuipian.png |
| 25628 | 白色花 | model/C1/L2/Model/L2_03_01/sm_longgong_di_02.FBX | 1 | t_longgong_hua_02.png |
| 25842 | 魔法帽 | model/sprite3d/sm_L10_youyijianzhengguan.fbx | 1 | t_L11_mofamao.png |
| 25844 | 密室大门 | model/sprite3d/sm_L11_mishidamen.FBX | 1 | t_L11_mishidamen_d.png |
| 25845 | 混沌星核 | model/sprite3d/sm_L11_hundunxinghe.FBX | 1 | t_L11_hundunxinghe_d.png |
| 25846 | 王者之剑 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian.png |
| 25847 | 王者之剑-剑坯 | model/sprite3d/sm_l11_wangzhezhijian_jianpei.FBX | 1 | t_l11_wangzhezhijian_jianpei.png |
| 25848 | 妖精金属 | model/sprite3d/sm_L11_yaolingjiashu.FBX | 1 | t_L11_yaojingjinshu_d.png |
| 25849 | 水球 | model/sprite3d/sm_L11_shuiqiu.FBX | 1 | t_L11_shuiqiu_d.png |
| 25891 | 水晶方块 | model/sprite3d/shuijingfangkuai.fbx | 1 | kuangdong_02.png |
| 26219 | 舔狗魔镜破碎 | model/sprite3d/sm_l10_jingzi.FBX | 1 | t_l10_jingziposui.png |
| 26290 | 魔药瓶（银） | model/C1/L7/Model/l7-02-02/sm_l7_myy_pingzi_02.FBX | 1 | t_l7_myy_pingzi_02.png |
| 26291 | 服装店（营地11-3） | model/C1/L10/Model/l10-03/sm_l8_ykz_chuchuangfang.fbx | 3 | t_l8_ykz_chuchuangfang_01.png, t_l8_hongwa_01.png, t_l7_tongyongxiaomen.png |
| 26292 | 水晶 | model/prop/BigWorld/L1/kuangdong/kuangdong_shuijing01.FBX | 1 | kuangdong_02.png |
| 26567 | 希斯发3D精灵 | - | 1 | shadows.png |
| 26607 | 王者之剑  蓝 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian_lan.png |
| 26608 | 王者之剑 紫 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian_zi.png |
| 26610 | 一份小抄 | model/sprite3d/sm_l12_xiaochao.fbx | 1 | t_l12_xiaochao.png |
| 26686 | 强化符文01 | model/sprite3d/sm_l12_qhfw.fbx | 1 | t_l12_qhfw.png |
| 26687 | 强化符文02 | model/sprite3d/sm_l12_qhfw.fbx | 1 | t_l12_qhfw.png |
| 26688 | 强化符文03 | model/sprite3d/sm_l12_qhfw.fbx | 1 | t_l12_qhfw.png |
| 26689 | 强化符文04 | model/sprite3d/sm_l12_qhfw.fbx | 1 | t_l12_qhfw.png |
| 26692 | 特斯拉时空跑车崭新版 | - | 1 | shadows.png |
| 26693 | 特斯拉时空跑车灰尘版 | - | 1 | shadows.png |
| 26736 | 马撕客的操作台 | model/C1/L8/Model/l8-01-01/sm_l8_jinlin_kzt.fbx | 2 | t_l8_jinlin_kzt_01.png, t_l8_jinlin_kzt_02.png |
| 26738 | 碎石障碍 | model/sprite3d/sm_l11_feixu.fbx | 1 | t_l11_feixu_03_shitou.png |
| 26753 | 魔法线圈 | model/sprite3d/sm_L12_mofaxianquan.fbx | 1 | t_L12_mofaxianquan.png |
| 26754 | 魔法乙醇汽油 | model/sprite3d/sm_L12_mofayichunqiyou.fbx | 1 | t_L12_mofayichunqiyou.png |
| 26755 | 特斯拉电塔 | model/sprite3d/sm_L12_tesiladianta.fbx | 1 | t_L12_tesiladianta.png |
| 26756 | 魔法钥匙待机 | model/sprite3d/sm_l12_yaoshi.fbx | 1 | t_l12_paoche_01.png |
| 26757 | 法阵的星星01 | model/sprite3d/sm_l12_szxx_01.fbx | 1 | t_l12_xingxing.png |
| 26758 | 法阵的星星02 | model/sprite3d/sm_l12_szxx_02.fbx | 1 | t_l12_xingxing.png |
| 26759 | 法阵的星星03 | model/sprite3d/sm_l12_szxx_03.fbx | 1 | t_l12_xingxing.png |
| 26760 | 法阵的星星04 | model/sprite3d/sm_l12_szxx_11.fbx | 1 | t_l12_xingxing.png |
| 26761 | 法阵的星星05 | model/sprite3d/sm_l12_fzxx_01.fbx | 1 | t_l12_xingxing.png |
| 26762 | 法阵的星星06 | model/sprite3d/sm_l12_fzxx_02.fbx | 1 | t_l12_xingxing.png |
| 26763 | 法阵的星星07 | model/sprite3d/sm_l12_fzxx_03.fbx | 1 | t_l12_xingxing.png |
| 26764 | 法阵的星星08 | model/sprite3d/sm_l12_fzxx_04.fbx | 1 | t_l12_xingxing.png |
| 26765 | 法阵的星星09 | model/sprite3d/sm_l12_fzxx_05.fbx | 1 | t_l12_xingxing.png |
| 26766 | 法阵的星星10 | model/sprite3d/sm_l12_fzxx_06.fbx | 1 | t_l12_xingxing.png |
| 26768 | 魔法钥匙发光 | model/sprite3d/sm_l12_yaoshi.fbx | 1 | t_l12_paoche_01.png |
| 26881 | 应有尽有还可以冥想盆 | model/sprite3d/sm_l12_mingxiangpen.fbx | 1 | t_l12_mingxiangpen.png |
| 26891 | 建材包裹 | model/sprite3d/sm_l7_jiancaibaoguo.fbx | 1 | t_l7_jiancaibaoguo.png |
| 26892 | 魔植包裹 | model/sprite3d/sm_l7_mozhibaoguo.fbx | 1 | t_l7_mozhibaoguo.png |
| 26918 | 希斯发未黑化3D精灵版 | - | 1 | shadows.png |
| 27083 | 特斯拉时空跑车发光 | - | 1 | shadows.png |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@skin.fbx<br>model/player/C_L7/jixiebiquanxiangche_jiexiebi/baoguo.fbx | 5 | jixiebi_02_D.png, t_l7_jiancaibaoguo.png, t_yj_quanxiangche_02.png, jixiebi_01_D.png, t_yj_quanxiangche_01.png |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@skin.fbx<br>model/player/C_L7/jixiebiquanxiangche_jiexiebi/baoguo.fbx | 5 | jixiebi_02_D.png, t_yj_quanxiangche_02.png, t_l7_mozhibaoguo.png, jixiebi_01_D.png, t_yj_quanxiangche_01.png |
| 27243 | 王者之剑终极 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian_zhongji.png |
| 27247 | 王者之剑寒冰特效 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian_lan.png |
| 27249 | 王者之剑火焰特效 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian.png |
| 27250 | 王者之剑空间魔法 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian_zi.png |
| 27251 | 王者之剑终极特效 | model/sprite3d/sm_l11_wangzhezhijian.FBX | 1 | t_l11_wangzhezhijian_zhongji.png |
| 27392 | 曼德拉草3D精灵 | - | 1 | shadows.png |
| 27393 | 矮人3D精灵 | - | 1 | shadows.png |
| 27394 | 魔法加特林 | model/sprite3d/sm_L9_ouyang_wuqi1.fbx | 1 | L9_ouyangnvdi_wuqi_D.png |
| 27414 | 傀儡小兵残骸 | model/sprite3d/sm_L12_kuileixiaobingcanhai.fbx | 2 | L12_kuileidunpai.png, t_L9_kuijiashouwei.png |
| 27547 | 魔药速递 龙痘疮 | model/C1/L8/Model/l8-03-02/sm_l8-03-01_wujian_01.FBX | 1 | - |
| 27548 | 魔药速递 炼魔药 | model/C1/L8/Model/l8-03-02/sm_l8-03-01_wujian_02.FBX | 3 | t_l2-03_db_03.png, t_l7_cao_02.png |
| 27551 | 队长魔法袍03_3D精灵 | - | 1 | shadows.png |
| 27552 | 雪球0_5_3D精灵 | - | 1 | shadows.png |
| 27553 | 桃子魔法袍_3D精灵 | - | 1 | shadows.png |
| 27554 | 乌拉乎魔法袍_3D精灵 | - | 1 | shadows.png |
| 27555 | 禾木魔法袍_3D精灵 | - | 1 | shadows.png |
| 27559 | 魔药速递 炼魔药取货区 | model/C1/L8/Model/l8-03-02/sm_l8-03-02_wujian_03.FBX | 1 | t_l8-03-01_wujian_04.png |
| 27693 | 毕业典礼横幅 | model/sprite3d/sm_l12_hengfu.fbx | 1 | t_l12_hengfu.png |
| 27694 | 毕业证书 | model/sprite3d/sm_l12_biyezhengshu.fbx | 1 | t_l12_biyezhengshu.png |
| 27695 | 气球装饰 | model/C1/L10/Model/l10-03-02/sm_l10_yqjzs_qiqiu01.FBX | 1 | t_l10_yqjzs_qiqiu.png |
| 27816 | 0 | model/sprite3d/sm_0.fbx | 1 | t_shuzi.png |
| 27817 | 1 | model/sprite3d/sm_1.fbx | 1 | t_shuzi.png |
| 27818 | 2 | model/sprite3d/sm_2.fbx | 1 | t_shuzi.png |
| 27819 | 3 | model/sprite3d/sm_3.fbx | 1 | t_shuzi.png |
| 27820 | 4 | model/sprite3d/sm_4.fbx | 1 | t_shuzi.png |
| 27821 | 5 | model/sprite3d/sm_5.fbx | 1 | t_shuzi.png |
| 27822 | 6 | model/sprite3d/sm_6.fbx | 1 | t_shuzi.png |
| 27823 | 7 | model/sprite3d/sm_7.fbx | 1 | t_shuzi.png |
| 27824 | 8 | model/sprite3d/sm_8.fbx | 1 | t_shuzi.png |
| 27825 | 9 | model/sprite3d/sm_9.fbx | 1 | t_shuzi.png |
| 27871 | 凸显框 | - | 1 | box_D.tga |
| 27956 | 智能小车混沌星核无超声传感 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@skin.FBX | 2 | t_l7_zhinengxiaoche.png, shadows.png |
| 28016 | 单格冰块 | model/C1/L4/Model/l4_03_01/sm_l4_bgc_dimian_02.fbx | 1 | t_l4_bgc_shitou_01.png |
| 28017 | 营地地砖 | model/C1/L4/Model/l4_04_01/sm_l4_gsgc_dbst01.fbx | 1 | t_l7_yingdi_dbyp01.png |
| 28055 | 雷达 | model/sprite3d/sm_l13_leida.fbx | 1 | t_l13_leida.png |
| 28056 | 袋装种子 | model/sprite3d/sm_l13_dzzz.FBX | 1 | t_l13_dzzz.png |
| 28057 | 冰块 | model/sprite3d/sm_l13_dj_bingkuai.fbx | 1 | t_l13_dj_bingkuai.png |
| 28058 | 可燃冰原始状态 | model/sprite3d/sm_l13_keranbing.fbx | 1 | t_l13_keranbing.png |
| 28059 | 椰子树 | model/sprite3d/sm_l13_yezishu.FBX | 1 | t_l13_yezishu.png |
| 28063 | 机械臂（装备） | model/sprite3d/sm_l13_jxb.FBX | 1 | t_l13_jxb.png |
| 28064 | 星际服 | model/sprite3d/sm_L13_xingjifu.FBX | 1 | t_L13_xingjifu.png |
| 28065 | 生物编码药剂粉 | - | 1 | t_L13shengwubianmayaoji_hong.png |
| 28066 | 生物编码药剂绿 | - | 1 | t_L13shengwubianmayaoji.png |
| 28067 | 普通探头待机状态 | model/sprite3d/sm_L13_nengyuantantou.FBX | 2 | t_L13_nengyuantantou_pingmu_D.png, t_L13_nengyuantantou_D.png |
| 28068 | 普通探头成功状态 | model/sprite3d/sm_L13_nengyuantantou.FBX | 2 | t_L13_nengyuantantou_pingmu_D.png, t_L13_nengyuantantou_D.png |
| 28069 | 普通探头工作状态 | model/sprite3d/sm_L13_nengyuantantou.FBX | 2 | t_L13_nengyuantantou_pingmu_D.png, t_L13_nengyuantantou_D.png |
| 28075 | 盲盒 | model/sprite3d/sm_l13_manghe.fbx | 1 | t_l13_manghe.png |
| 28077 | 合格板子 | model/sprite3d/sm_l13_hegeban.fbx | 1 | t_l13_hgb.png |
| 28078 | 电磁板 | model/sprite3d/sm_l13_tynb.fbx | 1 | t_l13_hgb.png |
| 28079 | 太阳能板02 | model/sprite3d/sm_l13_tynb.fbx | 1 | t_l13_hgb_02.png |
| 28080 | 组装材料 零件箱 | model/sprite3d/sm_l13_dzgjx.fbx | 1 | t_l13_dzgjx.png |
| 28101 | 能源探头待机状态 | model/sprite3d/sm_L13_putongtantou_01.FBX | 2 | t_L13_putongtantou_02.png, t_L13_putongtantou_01.png |
| 28102 | 能源探头工作状态 | model/sprite3d/sm_L13_putongtantou_01.FBX | 2 | t_L13_putongtantou_02.png, t_L13_putongtantou_01.png |
| 28103 | 能源探头成功状态 | model/sprite3d/sm_L13_putongtantou_01.FBX | 2 | t_L13_putongtantou_02.png, t_L13_putongtantou_01.png |
| 28108 | 魔药园风车建筑 | model/C1/L7/Model/l7-02-02/sm_l7_myy_fengche/sm_l7_myy_fengche.FBX | 1 | t_l7_myy_fengche.png |
| 28110 | 水泥地砖 | model/C1/L4/Model/l4_04_01/sm_l4_gsgc_dbst01.fbx | 1 | t_l13_dizhuan.png |
| 28133 | 队长小屋 简易太空舱 | model/C1/L13/Model/l13-03-01/sm_l13_dzxw.fbx | 2 | t_l13_dzxw_b.png, t_l13_dzxw_a.png |
| 28134 | 男生住宅 | model/C1/L13/Model/l13-03-01/sm_l13_hmxw.fbx | 2 | t_l13_hmxw_b.png, t_l13_hmxw_a.png |
| 28257 | 材料板 | model/sprite3d/sm_l13_bingkuai.fbx | 1 | t_l13_bingkuai.png |
| 28265 | 布 | model/sprite3d/sm_l13_bu.fbx | 1 | t_l13_bu.png |
| 28268 | 材料条1 | model/sprite3d/sm_l13_bingkuai001.fbx | 1 | t_l13_bingkuai.png |
| 28269 | 材料条2 | model/sprite3d/sm_l13_bingkuai002.fbx | 1 | t_l13_bingkuai.png |
| 28270 | 材料条3 | model/sprite3d/sm_l13_bingkuai003.fbx | 1 | t_l13_bingkuai.png |
| 28271 | 电磁板02 | model/sprite3d/sm_l13_tynb02.fbx | 1 | t_l13_hgb.png |
| 28274 | 机械物件02 | model/prop/BigWorld/L2/jiuyou/002.FBX | 1 | 1.psd |
| 28633 | 避雷针塔 | model/sprite3d/sm_l14_blzt.fbx | 1 | t_l14_blzt.png |
| 28665 | 螺蛳粉锅 | model/sprite3d/sm_l15_lsfg.fbx | 1 | t_l15_lsfg.png |
| 28666 | 墙上涂鸦 | model/sprite3d/sm_l15_qsty.fbx | 1 | t_l15_qsty.png |
| 28668 | 等离子发射器 | model/sprite3d/sm_L13_denglizifasheqi.fbx | 1 | t_L13_denglizifasheqi_D.png |
| 28669 | 制造车间 | model/C1/L6/Model/l6_04_01/sm_l6_hexin_02.FBX | 2 | t_l6_hexin_qiangbi.png, t_l6_hexin_02.png |
| 28670 | 蓄电池组升级前 | model/sprite3d/sm_l13_dcz_01.fbx | 2 | t_l13_dcz.png, t_l13_dcz_02.png |
| 28671 | 蓄电池组升级后 | model/sprite3d/sm_l13_dcz_02.fbx | 2 | t_l13_dcz_01.png, t_l13_dcz_03.png |
| 28672 | 蓄电池组电力不足 | model/sprite3d/sm_l13_dcz_03.fbx | 2 | t_l13_dcz_01.png, t_l13_dcz_04.png |
| 28673 | 判断指示灯 红色 | model/sprite3d/sm_l15_pdzsd_04.FBX | 1 | t_l15_pdzsd_04.png |
| 28674 | 蓄电池组充满电 | model/sprite3d/sm_l13_dcz_04.fbx | 2 | t_l13_dcz_05.png, t_l13_dcz_01.png |
| 28675 | 判断指示灯 待机 | model/sprite3d/sm_l15_pdzsd_03.FBX | 1 | t_l15_pdzsd_03.png |
| 28676 | 判断指示灯 黄色 | model/sprite3d/sm_l15_pdzsd_02.FBX | 1 | t_l15_pdzsd_02.png |
| 28677 | 判断指示灯 绿色 | model/sprite3d/sm_l15_pdzsd_01.FBX | 1 | t_l15_pdzsd_01.png |
| 28699 | 扁易拉罐 | model/sprite3d/sm_l15_pylg.fbx | 1 | t_l15_pylg.png |
| 28700 | 香蕉皮 | model/sprite3d/sm_l15_xjp.fbx | 1 | t_l15_xjp.png |
| 28737 | 影子 | - | 1 | t_l13_shadows_01.png |
| 28738 | 一篮子土块 | model/sprite3d/sm_l15_yltk.FBX | 1 | t_l15_yltk.png |
| 28749 | 陨石 | model/sprite3d/sm_l9_dj_cailiaodui_04.FBX | 1 | t_l9_jianjiaoji.png |
| 28754 | 神经 | model/sprite3d/sm_l5_shengzhi.FBX | 1 | t_l14_shenjing.png |
| 28936 | 桌子01-关卡 | model/C1/L5/Model/l5_04_02/sm_l5_gddpn_jiazi_02.FBX | 1 | t_l5_gddpn_jiazi.png |
| 28937 | 桌子02-关卡 | model/C1/L5/Model/l5_04_02/sm_l5_gddpn_jiazi_01.FBX | 1 | t_l5_gddpn_jiazi.png |
| 28938 | 桌子03-关卡 | model/C1/L5/Model/l5_04_02/sm_l5_gddpn_jiazi_03.FBX | 1 | t_l5_gddpn_jiazi_03.png |
| 28952 | 出库机 | model/sprite3d/sm_l14_ckj.FBX | 1 | t_l14_ckj.png |
| 28996 | 核心材料 | model/sprite3d/sm_L13_hexincailiao.fbx | 1 | t_L12_mofaxianquan.png |
| 28999 | 全向车机械臂货框颜色传感器 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@skin.fbx<br>model/player/C_L7/jixiebiquanxiangche_jiexiebi/baoguo.fbx | 5 | jixiebi_02_D.png, t_l7_jiancaibaoguo.png, t_yj_quanxiangche_02.png, jixiebi_01_D.png, t_yj_quanxiangche_01.png |
| 29110 | 检测机器 | model/sprite3d/SM_pingjijiqiz_a.FBX | 1 | T_pingjijiqi.png |
| 29136 | 测试灰地砖 | model/sprite3d/sm_l13_dizhuan.fbx | 1 | t_l13_huidizhuan.png |
| 29137 | 测试灰地砖02 | model/C1/L4/Model/l4_04_01/sm_l4_gsgc_dbst01.fbx | 1 | t_l13_dizhuan.png |
| 29140 | 窑炉    窑炉口1 | model/C1/L5/Model/l5_03_02/sm_l5_zqsn_08@anim.FBX | 1 | t_l5_zqsn_03.png |
| 29141 | 窑炉口2 | model/sprite3d/sm_l15_yaoluko02.fbx | 1 | t_l15_ylk.png |
| 29160 | 石墨烯避雷针塔 01 | model/sprite3d/sm_l14_blzt_hei_01.fbx | 1 | t_l14_blzt_hei.png |
| 29225 | 传送履带 | model/sprite3d/sm_chuansonglvdai.fbx | 1 | t_chuansonglvdai.png |
| 29227 | 挂衣架 | model/sprite3d/sm_L15_guayijia.fbx | 1 | t_L15_guayijia.png |
| 29228 | 防爆盾牌 | model/sprite3d/sm_l14_fangbaodunpai.FBX | 1 | t_l14_fangbaodunpai.png |
| 29247 | 新隔热材料 | - | 1 | t_l13_@.png |
| 29297 | 漫波神庙大门 | model/player/C_L14/manboshenmiaodamen/manboshenmiaodamen@anim.fbx | 3 | t_l14_mbsd_texiao.png, t_l14_mbsd_rkjz_02.png, t_l14_mbsd_rkjz_01.png |
| 29298 | 漫波大神庙密码门 | model/player/C_L14/manboshenmiao_mimamen/mbsd_mimamen@anim.fbx | 4 | t_l15_mbsd_rkjz_03.png, t_l14_mbsd_texiao.png, t_l15_mbsd_rkjz_02.png, t_l15_mbsd_rkjz_01.png |
| 29301 | 榴莲 | model/sprite3d/sm_l14_liulian.FBX | 1 | t_l14_liulian.png |
| 29314 | 树脂 | model/sprite3d/sm_l14_shuzhi.fbx | 1 | t_l14_shuzhi.png |
| 29315 | 硼砂 | model/sprite3d/sm_l14_pengsha.fbx | 1 | t_l14_pengsha.png |
| 29333 | 计时器 | model/sprite3d/sm_l14_jshiqi.fbx | 1 | t_l14_jshiqi.png |
| 29633 | 马车 | - | 1 | shadows.png |
| 29649 | super钻头 | model/sprite3d/sm_l14_zuantou.FBX | 1 | t_l15_jiapian.png |
| 29650 | 绝缘体装甲片 | model/sprite3d/sm_l15_jiapian.FBX | 1 | t_l15_jiapian.png |
| 29651 | EMP | model/sprite3d/sm_l15_emp.FBX | 1 | t_l15_emp.png |
| 29661 | 曼德拉草_捕狼草 | - | 1 | shadows.png |
| 29663 | 商人货车白 | - | 1 | shadows.png |
| 29664 | 商人货车黑 | - | 1 | shadows.png |
| 29665 | 休眠舱-休眠状态 | model/sprite3d/sm_l15_xiumiancang.FBX | 1 | t_l15_xiumiancang.png |
| 29671 | 配置机器 履带 | model/sprite3d/sm_l14_pzjq_02.FBX | 2 | t_l14_pzjq_c.png, t_l14_pzjq_b.png |
| 29672 | 配置机器 机身 | model/sprite3d/sm_l14_pzjq_01.FBX | 2 | t_l14_pzjq_b.png, t_l14_pzjq_a.png |
| 29675 | 护卫机甲 | - | 1 | shadows.png |
| 29801 | 弹坑 | model/sprite3d/sm_l15_yunshikeng.FBX | 1 | t_l15_yunshikeng.png |
| 29805 | 马车黄色有货物 | - | 1 | shadows.png |
| 29807 | 马车白色有货物 | - | 1 | shadows.png |
| 29809 | 马车黑色有货物 | - | 1 | shadows.png |
| 29819 | 灰尘 01 | model/sprite3d/sm_l14_shadui_01.fbx | 1 | t_l14_shadui_01.png |
| 29820 | 灰尘 02 | model/sprite3d/sm_l14_shadui_02.fbx | 1 | t_l14_shadui_01.png |
| 29821 | 曼波塔 | - | 1 | shadows.png |
| 29824 | 数字密码锁 设计说明书 | model/sprite3d/sm_l14_sjsms.fbx | 1 | t_l14_sjsms.png |
| 29827 | 压缩饼干 | model/sprite3d/sm_L14_yasuobinggan.fbx | 1 | t_L14_yasuobinggan_D.png |
| 29828 | 医药包 | model/sprite3d/sm_L14_yiyaobao.fbx | 1 | t_L14_yiyaobao_D.png |
| 29830 | 门禁卡 | model/sprite3d/sm_l14_mjk.fbx | 1 | t_l14_mjk.png |
| 29842 | 小鸡的装药碗 | model/sprite3d/sm_l14_zhuangyaowan.FBX | 1 | t_l14_zhuangyaowan.png |
| 29933 | 红土块 | model/sprite3d/sm_l15_yltk.FBX | 1 | t_l15_hongtukuai.png |
| 29934 | 黑土块 | model/sprite3d/sm_l9_dj_cailiaodui_02.FBX | 1 | t_l9_jianjiaoji02.png |
| 29935 | 煤球2 | - | 1 | t_l15_1.png |
| 29936 | 煤球7 | - | 1 | t_l15_7.png |
| 30101 | 碎盲盒 | model/sprite3d/sm_l14_smh.fbx | 1 | t_l14_manghe_sui.png |
| 30105 | no箱 | model/sprite3d/sm_l14_xiangzi.fbx | 1 | t_l14_no.png |
| 30106 | yes箱 | model/sprite3d/sm_l14_xiangzi.fbx | 1 | t_l14_yes.png |
| 30107 | 传送带 | model/sprite3d/sm_l14_csd.fbx | 2 | t_l14_jiqi_b.png, t_l14_jiqi_c.png |
| 30189 | 小核桃emp | - | 1 | shadows.png |
| 30192 | 普通炮弹 | model/sprite3d/sm_l14_ptpd.FBX | 1 | t_l14_ptpd.png |
| 30305 | 漫波塔说明书 | model/sprite3d/sm_l15_mbsms.fbx | 1 | t_l15_mbsms.png |
| 30306 | 矿泉水 | model/sprite3d/sm_l15_ljd_08.FBX | 1 | t_l15_ljd.png |
| 30455 | 榴莲大炮 | model/sprite3d/sm_l14_lldp.FBX | 1 | t_l14_lldp.png |
| 30459 | 胶囊存储器 | model/sprite3d/sm_L14_jiaonangchucunqi.fbx | 1 | t_L14_jiaonangchucunqi_D.png |
| 30472 | 红土块02 | model/sprite3d/sm_l15_htk.FBX | 1 | t_l15_hongtukuai.png |
| 30473 | 一篮子石墨 | model/sprite3d/sm_gk_lanzi.fbx | 1 | T_lianzaocailiao.png |
| 30474 | yes箱子 | - | 1 | t_yes.png |
| 30475 | no箱子 | - | 1 | t_no.png |
| 30670 | 曼波塔趴地上 | - | 1 | shadows.png |
| 30823 | 冰沙  粉色 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_fen.fbx | 1 | t_L16_bingsh_d.png |
| 30824 | 冰沙  黄色 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_huang.fbx | 1 | t_L16_bingsh_d.png |
| 30825 | 冰沙  蓝色 | model/C1/L2/Model/L2_01_01/sm_mixuebingniu_lan.fbx | 1 | t_L16_bingsh_d.png |

## 动画详情：可精确拿到 duration 的 clip

> 只列出 FBX.meta 里有 clipAnimations 配置的动画；duration = (lastFrame - firstFrame) / 30fps。

| AssetId | 物件 | state 名 | 循环 | 时长(s) | Motion FBX |
|---------|------|---------|------|---------|-----------|
| 12582 | 宝箱 | open | 一次 | 2.33 | model/player/baoxiang/baoxiang@open.fbx |
| 12582 | 宝箱 | guan | 循环 | 0.67 | model/player/baoxiang/baoxiang@guan.fbx |
| 12588 | 普通机械螃蟹 | idle | 循环 | 1.60 | model/player/A1.1/pangxie/jixiepangxie@idle.FBX |
| 12588 | 普通机械螃蟹 | idle_shoushang | 循环 | 1.60 | model/player/A1.1/pangxie/jixiepangxie@idle_shoushang.fbx |
| 12588 | 普通机械螃蟹 | walk | 循环 | 1.00 | model/player/A1.1/pangxie/jixiepangxie@walk.FBX |
| 14680 | 猫雷达 | leidachuxian | 一次 | 1.17 | model/player/C_L2/maoleida/maoleida@leidachuxian.FBX |
| 14680 | 猫雷达 | leidadaiji | 一次 | 1.00 | model/player/C_L2/maoleida/maoleida@leidadaiji.FBX |
| 14680 | 猫雷达 | idle | 循环 | 0.56 | model/player/C_L2/maoleida/maoleida@idle.FBX |
| 14721 | 黄牛_3D | fangentou_loop | 循环 | 0.60 | model/prop/BigWorld/L1/juese/huangniu/huangniu@fangentou.FBX |
| 14721 | 黄牛_3D | run | 循环 | 0.80 | model/prop/BigWorld/L1/juese/huangniu/huangniu@run.fbx |
| 14721 | 黄牛_3D | idle | 循环 | 1.60 | model/prop/BigWorld/L1/juese/huangniu/huangniu@idle.fbx |
| 14721 | 黄牛_3D | fangentou_end | 一次 | 0.40 | model/prop/BigWorld/L1/juese/huangniu/huangniu@fangentou.FBX |
| 14721 | 黄牛_3D | zhengzha | 循环 | 2.50 | model/prop/BigWorld/L1/juese/huangniu/huangniu@zhengzha.fbx |
| 14721 | 黄牛_3D | fangentou_start | 一次 | 0.13 | model/prop/BigWorld/L1/juese/huangniu/huangniu@fangentou.FBX |
| 14721 | 黄牛_3D | daoxiaxunhuan | 循环 | 1.67 | model/prop/BigWorld/L1/juese/huangniu/huangniu@daoxiaxunhuan.FBX |
| 14721 | 黄牛_3D | chuanqi | 循环 | 2.00 | model/prop/BigWorld/L1/juese/huangniu/huangniu@chuanqi.fbx |
| 14721 | 黄牛_3D | dakeshui | 循环 | 2.00 | model/prop/BigWorld/L1/juese/huangniu/huangniu@dakeshui.FBX |
| 14721 | 黄牛_3D | idle_jingya | 循环 | 1.60 | model/prop/BigWorld/L1/juese/huangniu/huangniu@idle_jingya.fbx |
| 14721 | 黄牛_3D | beibang | 循环 | 1.60 | model/prop/BigWorld/L1/juese/huangniu/huangniu@beibang.fbx |
| 14721 | 黄牛_3D | walk | 循环 | 1.20 | model/prop/BigWorld/L1/juese/huangniu/huangniu@walk.fbx |
| 14722 | 队长_3D | run | 循环 | 0.80 | model/player/A1.1/nanhai/nanhai@run.fbx |
| 14722 | 队长_3D | walk | 循环 | 1.07 | model/player/A1.1/nanhai/nanhai@walk.fbx |
| 14722 | 队长_3D | idle | 循环 | 1.60 | model/player/A1.1/nanhai/nanhai@idle.fbx |
| 14722 | 队长_3D | zuo_idle | 循环 | 1.60 | model/player/A1.1/nanhai/nanhai@zuo_idle.FBX |
| 14723 | 展喵_3D | run | 循环 | 0.80 | model/player/A1.1/zhanmiao/zhanmiao@run.fbx |
| 14723 | 展喵_3D | qienuo_xuanyun | 循环 | 1.60 | model/player/A1.1/zhanmiao/zhanmiao@qienuo_xuanyun.FBX |
| 14723 | 展喵_3D | xusheng | 循环 | 2.17 | model/player/A1.1/zhanmiao/zhanmiao@xusheng.FBX |
| 14723 | 展喵_3D | xuruo_loop | 循环 | 1.60 | model/player/A1.1/zhanmiao/zhanmiao@xuruo_loop.FBX |
| 14723 | 展喵_3D | idle02 | 循环 | 1.60 | model/player/A1.1/zhanmiao/zhanmiao@idle02.FBX |
| 14723 | 展喵_3D | idle | 循环 | 1.60 | model/player/A1.1/zhanmiao/zhanmiao@idle.fbx |
| 14723 | 展喵_3D | beixi | 循环 | 0.53 | model/player/A1.1/zhanmiao/zhanmiao@beixi.FBX |
| 14723 | 展喵_3D | walk | 循环 | 1.07 | model/player/A1.1/zhanmiao/zhanmiao@walk.fbx |
| 14723 | 展喵_3D | qienuo_idle | 循环 | 1.60 | model/player/A1.1/zhanmiao/zhanmiao@qienuo_idle.FBX |
| 14723 | 展喵_3D | chuanqi | 循环 | 2.00 | model/player/A1.1/zhanmiao/zhanmiao@chuanqi.fbx |
| 14723 | 展喵_3D | dianzan | 一次 | 1.83 | model/player/A1.1/zhanmiao/zhanmiao@dianzan.FBX |
| 14724 | 小核桃_3D | idle | 循环 | 1.73 | model/player/A1.1/xiaohetao02/xiaohetao@idle02.fbx |
| 14724 | 小核桃_3D | run | 循环 | 0.67 | model/player/A1.1/xiaohetao02/xiaohetao@run02.FBX |
| 14724 | 小核桃_3D | danshoubeng | 循环 | 2.27 | model/player/A1.1/xiaohetao02/xiaohetao@danshoubeng.FBX |
| 14724 | 小核桃_3D | walk | 循环 | 1.07 | model/player/A1.1/xiaohetao02/xiaohetao@walk2.fbx |
| 14724 | 小核桃_3D | daoli_run | 循环 | 0.40 | model/player/A1.1/xiaohetao02/xiaohetao@daoli_run.FBX |
| 14724 | 小核桃_3D | jingxia | 一次 | 2.00 | model/player/A1.1/xiaohetao02/xiaohetao@sleep.fbx |
| 14724 | 小核桃_3D | sleep_strat | 一次 | 1.07 | model/player/A1.1/xiaohetao02/xiaohetao@sleep.fbx |
| 14724 | 小核桃_3D | yundao_shuijiao | 循环 | 1.33 | model/player/A1.1/xiaohetao02/xiaohetao@yundao_shuijiao.FBX |
| 14724 | 小核桃_3D | daoli_idle | 循环 | 1.73 | model/player/A1.1/xiaohetao02/xiaohetao@daoli_idle.FBX |
| 14724 | 小核桃_3D | danxiguidi | 循环 | 1.60 | model/player/A1.1/xiaohetao02/xiaohetao@danxiguidi.FBX |
| 14724 | 小核桃_3D | taishou_end | 一次 | 0.37 | model/player/A1.1/xiaohetao02/xiaohetao@taishou.fbx |
| 14724 | 小核桃_3D | beixi | 循环 | 0.67 | model/player/A1.1/xiaohetao02/xiaohetao@beixi.FBX |
| 14724 | 小核桃_3D | taishou | 一次 | 0.97 | model/player/A1.1/xiaohetao02/xiaohetao@taishou.fbx |
| 14724 | 小核桃_3D | taishou_loop | 循环 | 1.00 | model/player/A1.1/xiaohetao02/xiaohetao@taishou.fbx |
| 14724 | 小核桃_3D | zuo_idle | 循环 | 1.73 | model/player/A1.1/xiaohetao02/xiaohetao@zuo_idle.FBX |
| 14724 | 小核桃_3D | sleep | 循环 | 1.33 | model/player/A1.1/xiaohetao02/xiaohetao@sleep.fbx |
| 14724 | 小核桃_3D | dangfeng | 循环 | 1.73 | model/player/A1.1/xiaohetao02/xiaohetao@dangfeng.fbx |
| 14724 | 小核桃_3D | chuanqi | 循环 | 2.00 | model/player/A1.1/xiaohetao02/xiaohetao@chuanqi.fbx |
| 14724 | 小核桃_3D | kanxianshiping | 循环 | 1.73 | model/player/A1.1/xiaohetao02/xiaohetao@kanxianshiping.FBX |
| 14725 | 核桃机甲_3D | run | 循环 | 0.80 | model/player/A1.1/hetaojijia/hetaojijia@run.fbx |
| 14725 | 核桃机甲_3D | gui_idle | 循环 | 1.33 | model/player/A1.1/hetaojijia/hetaojijia@gui_idle.fbx |
| 14725 | 核桃机甲_3D | dianchidun_idle | 循环 | 1.33 | model/player/A1.1/hetaojijia/hetaojijia@dianchidunidle.FBX |
| 14725 | 核桃机甲_3D | idle | 循环 | 1.60 | model/player/A1.1/hetaojijia/hetaojijia@idle.fbx |
| 14725 | 核桃机甲_3D | walk | 循环 | 1.33 | model/player/A1.1/hetaojijia/hetaojijia@walk.fbx |
| 14725 | 核桃机甲_3D | tuiguangbo | 循环 | 1.73 | model/player/A1.1/hetaojijia/hetaojijia@tuiguangbo.FBX |
| 14727 | 茶杯盖子 | idle | 循环 | 1.07 | model/player/C_L2/chabeigai/gaizi@idle.FBX |
| 14727 | 茶杯盖子 | walk | 循环 | 1.00 | model/player/C_L2/chabeigai/gaizi@walk.FBX |
| 14727 | 茶杯盖子 | gaizhu | 循环 | 1.07 | model/player/C_L2/chabeigai/gaizi@gaizhu.FBX |
| 16090 | l4门 | kaimenidle | 循环 | 3.33 | model/player/C_L4/men/l4_gsgc_men@kaimenidle.FBX |
| 16090 | l4门 | idle | 循环 | 3.33 | model/player/C_L4/men/l4_gsgc_men@idle.FBX |
| 16356 | 水池盖子 | idle | 循环 | 0.07 | model/player/C_L4/shuichigaizi/l4_shuichigaizi@idle.FBX |
| 16406 | 红温保安 | idle | 循环 | 1.60 | model/player/C_L4/gongchanganbao/gongchanganbao@idle.FBX |
| 16406 | 红温保安 | walk | 循环 | 1.07 | model/player/C_L4/gongchanganbao/gongchanganbao@walk.FBX |
| 16406 | 红温保安 | run | 循环 | 0.60 | model/player/C_L4/gongchanganbao/gongchanganbao@run.FBX |
| 16407 | 红温食人花 | fengkuangyaobai | 循环 | 0.53 | model/player/A1.1/L1_shirenhua/shirenhua@fengkuangyaobai.FBX |
| 16407 | 红温食人花 | bizuihujiu | 循环 | 1.33 | model/player/A1.1/L1_shirenhua/shirenhua@bizuihujiu.FBX |
| 16407 | 红温食人花 | bizuiidle | 循环 | 1.33 | model/player/A1.1/L1_shirenhua/shirenhua@bizuiidle.FBX |
| 16407 | 红温食人花 | zhangzuiidle | 循环 | 1.33 | model/player/A1.1/L1_shirenhua/shirenhua@zhangzuiidle.FBX |
| 16407 | 红温食人花 | yao | 一次 | 1.00 | model/player/A1.1/L1_shirenhua/shirenhua@yao.FBX |
| 16408 | 红温扫地鲲 | jiangzhi_start | 一次 | 1.67 | model/player/C_L4/saodikun/saodikun@jiangzhi.FBX |
| 16408 | 红温扫地鲲 | zhangzuidaiji | 循环 | 1.60 | model/player/C_L4/saodikun/saodikun@zhangzuidaiji.FBX |
| 16408 | 红温扫地鲲 | jiangzhi_end | 一次 | 1.40 | model/player/C_L4/saodikun/saodikun@jiangzhi.FBX |
| 16408 | 红温扫地鲲 | idle | 循环 | 1.60 | model/player/C_L4/saodikun/saodikun@idle.FBX |
| 16408 | 红温扫地鲲 | run | 循环 | 0.67 | model/player/C_L4/saodikun/saodikun@run.FBX |
| 16408 | 红温扫地鲲 | walk | 循环 | 1.07 | model/player/C_L4/saodikun/saodikun@walk.FBX |
| 16408 | 红温扫地鲲 | jiangzhi_idle | 循环 | 1.33 | model/player/C_L4/saodikun/saodikun@jiangzhi_idle.FBX |
| 16408 | 红温扫地鲲 | shoutizi | 一次 | 1.97 | model/player/C_L4/saodikun/saodikun@shoutizi.FBX |
| 16409 | 红温机械狗仔 | run | 循环 | 0.53 | model/player/C_L4/jixiegouzhai_V01/jixiegouzhai_V01@run.FBX |
| 16409 | 红温机械狗仔 | walk | 循环 | 1.07 | model/player/C_L4/jixiegouzhai_V01/jixiegouzhai_V01@walk.FBX |
| 16409 | 红温机械狗仔 | idle | 循环 | 1.60 | model/player/C_L4/jixiegouzhai_V01/jixiegouzhai_V01@idle.FBX |
| 16410 | 红温螃蟹 | idle | 循环 | 1.60 | model/player/A1.1/pangxie/jixiepangxie@idle.FBX |
| 16410 | 红温螃蟹 | idle_shoushang | 循环 | 1.60 | model/player/A1.1/pangxie/jixiepangxie@idle_shoushang.fbx |
| 16410 | 红温螃蟹 | walk | 循环 | 1.00 | model/player/A1.1/pangxie/jixiepangxie@walk.FBX |
| 16411 | 朱雀 | kaixing | 循环 | 1.33 | model/player/C_L4/zhuque/zhuque@kaixing.FBX |
| 16411 | 朱雀 | tiedi_walk | 循环 | 1.07 | model/player/C_L4/zhuque/L4_zhuque@tiedi_walk.FBX |
| 16411 | 朱雀 | zhanli_idle | 循环 | 1.60 | model/player/C_L4/zhuque/L4_zhuque@zhanli_idle.FBX |
| 16411 | 朱雀 | idle | 循环 | 1.30 | model/player/C_L4/zhuque/zhuque@idle.FBX |
| 16411 | 朱雀 | walk | 循环 | 1.03 | model/player/C_L4/zhuque/zhuque@walk.FBX |
| 16411 | 朱雀 | daku | 循环 | 1.33 | model/player/C_L4/zhuque/zhuque@daku.FBX |
| 16411 | 朱雀 | run | 循环 | 0.67 | model/player/C_L4/zhuque/zhuque@run.FBX |
| 16413 | 白虎 | idle | 循环 | 1.60 | model/player/C_L4/baihu/baihu@idle.FBX |
| 16413 | 白虎 | run | 循环 | 0.53 | model/player/C_L4/baihu/baihu@run.FBX |
| 16413 | 白虎 | walk | 循环 | 1.07 | model/player/C_L4/baihu/baihu@walk.FBX |
| 16599 | 闸门开关 | zhamenkaiguan_dakai | 一次 | 0.53 | model/player/C_L5/zhamenkaiguan/zhamenkaiguan@anim.FBX |
| 16599 | 闸门开关 | zhamenkaiguan_dakaidaiji | 一次 | 0.03 | model/player/C_L5/zhamenkaiguan/zhamenkaiguan@anim.FBX |
| 16599 | 闸门开关 | zhamenkaiguan_idle | 一次 | 0.07 | model/player/C_L5/zhamenkaiguan/zhamenkaiguan@anim.FBX |
| 16980 | 卡皮巴拉大炮发射炮弹 | idle | 循环 | 1.60 | model/player/C_L5/kapibaladapao/kapibaladapao@idle.FBX |
| 16981 | 时日环 | anim | 循环 | 2.00 | model/player/C_L5/shirihuan/shirihuan@anim.FBX |
| 16987 | 游动浮光鲤 | youdong | 循环 | 0.80 | model/player/C_L5/fuguangli/fuguangli@youdong.FBX |
| 16987 | 游动浮光鲤 | idle | 循环 | 2.00 | model/player/C_L5/fuguangli/fuguangli@idle.FBX |
| 17009 | 打开待机武器箱 | dakai_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@dakai_idle.fbx |
| 17009 | 打开待机武器箱 | bihe_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@bihe_idle.fbx |
| 17016 | 蒸汽无人机 | walk | 循环 | 2.00 | model/player/C_L4/zhengqiwurenji/zhengqiwurenji.FBX |
| 17016 | 蒸汽无人机 | idle | 循环 | 2.00 | model/player/C_L4/zhengqiwurenji/zhengqiwurenji.FBX |
| 17016 | 蒸汽无人机 | run | 循环 | 2.00 | model/player/C_L4/zhengqiwurenji/zhengqiwurenji.FBX |
| 17016 | 蒸汽无人机 | zhengqiwurenji_anim | 循环 | 2.00 | model/player/C_L4/zhengqiwurenji/zhengqiwurenji.FBX |
| 17274 | 发光时空之眼 | idle | 循环 | 2.00 | model/player/C_L5/shikongzhiyan/shikongzhiyan@idle.FBX |
| 17965 | 嘟嘟车 | idle | 循环 | 2.00 | model/player/C_L6/duduche/duduche@idle.FBX |
| 17965 | 嘟嘟车 | move | 循环 | 1.33 | model/player/C_L6/duduche/duduche@move.FBX |
| 17981 | 监狱门 | kaimen | 一次 | 2.33 | model/C1/L6/Model/l6_03_02/jianyumen/jianyudamen@anim.FBX |
| 17990 | 检测狗 | idle | 循环 | 1.60 | model/player/C_L6/jiancegou/jianchegou@idle.FBX |
| 17990 | 检测狗 | run | 循环 | 0.53 | model/player/C_L6/jiancegou/jianchegou@run.FBX |
| 17990 | 检测狗 | walk | 循环 | 1.07 | model/player/C_L6/jiancegou/jianchegou@walk.FBX |
| 18014 | 天穹仪 | shaomiao | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@shaomiao.FBX |
| 18014 | 天穹仪 | zuoyouhuangdong | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@zuoyouhuangdong.FBX |
| 18014 | 天穹仪 | idle | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@idle.FBX |
| 18016 | 新版天穹仪 | shaomiao | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@shaomiao.FBX |
| 18016 | 新版天穹仪 | zuoyouhuangdong | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@zuoyouhuangdong.FBX |
| 18016 | 新版天穹仪 | idle | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@idle.FBX |
| 18020 | 投射土豆炮弹的蘑菇土豆天使炮 | idle | 循环 | 1.60 | model/player/C_L6/mogutudoutianshipao/mogutudoutianshipao@idle.FBX |
| 18022 | 发射脉冲弹菠萝西瓜脉冲弹 | idle | 循环 | 1.60 | model/player/C_L6/boluoxiguamaichongdan/boluoxiguamaichongdan@idle.FBX |
| 18327 | 鲁班锁 | idle | 循环 | 2.00 | model/player/C_L2/lubansuo/lubansuo@idle.FBX |
| 18530 | 天穹仪破碎版 | shaomiao | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@shaomiao.FBX |
| 18530 | 天穹仪破碎版 | zuoyouhuangdong | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@zuoyouhuangdong.FBX |
| 18530 | 天穹仪破碎版 | idle | 循环 | 1.60 | model/player/C_L6/tianqiongyi/sm_l6_tianqiongyi@idle.FBX |
| 18531 | 嘟嘟车+卡皮巴拉司机 | idle | 循环 | 1.33 | model/player/C_L6/duduche_chengke/duduche+sj@anim.FBX |
| 18531 | 嘟嘟车+卡皮巴拉司机 | move | 循环 | 1.33 | model/player/C_L6/duduche_chengke/duduche+sj@anim.FBX |
| 18532 | 嘟嘟车+乘客 | idle | 循环 | 1.33 | model/player/C_L6/duduche_chengke/duduche+chengke@skin.FBX |
| 18532 | 嘟嘟车+乘客 | move | 循环 | 1.33 | model/player/C_L6/duduche_chengke/duduche+chengke@skin.FBX |
| 18646 | 食人花 | fengkuangyaobai | 循环 | 0.53 | model/player/A1.1/L1_shirenhua/shirenhua@fengkuangyaobai.FBX |
| 18646 | 食人花 | bizuihujiu | 循环 | 1.33 | model/player/A1.1/L1_shirenhua/shirenhua@bizuihujiu.FBX |
| 18646 | 食人花 | bizuiidle | 循环 | 1.33 | model/player/A1.1/L1_shirenhua/shirenhua@bizuiidle.FBX |
| 18646 | 食人花 | zhangzuiidle | 循环 | 1.33 | model/player/A1.1/L1_shirenhua/shirenhua@zhangzuiidle.FBX |
| 18646 | 食人花 | yao | 一次 | 1.00 | model/player/A1.1/L1_shirenhua/shirenhua@yao.FBX |
| 18647 | 蒸汽破空 | run | 循环 | 0.53 | model/player/C_L4/zhengqipokong/zhengqipokong@run.FBX |
| 18647 | 蒸汽破空 | idle | 循环 | 1.60 | model/player/C_L4/zhengqipokong/zhengqipokong@idle.FBX |
| 18647 | 蒸汽破空 | walk | 循环 | 1.07 | model/player/C_L4/zhengqipokong/zhengqipokong@walk.FBX |
| 18652 | 坦克 | yidong | 循环 | 0.67 | model/player/C_L6/tanke/tanke@yidong.fbx |
| 18652 | 坦克 | idle | 循环 | 2.00 | model/player/C_L6/tanke/tanke@idle.fbx |
| 19851 | 全向车 | xiangzuopingyi | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@xiangzuopingyi.FBX |
| 19851 | 全向车 | idle | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@idle.FBX |
| 19851 | 全向车 | youzhuan | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@youzhuan.FBX |
| 19851 | 全向车 | run | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@run.FBX |
| 19851 | 全向车 | zuozhuan | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@zuozhuan.FBX |
| 20709 | 全向车_外卖 | xiangzuopingyi | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@xiangzuopingyi.FBX |
| 20709 | 全向车_外卖 | idle | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@idle.FBX |
| 20709 | 全向车_外卖 | youzhuan | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@youzhuan.FBX |
| 20709 | 全向车_外卖 | run | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@run.FBX |
| 20709 | 全向车_外卖 | zuozhuan | 循环 | 2.00 | model/player/A1.1/quanxiangche/yingjian_quanxiangche@zuozhuan.FBX |
| 20850 | 魔法马车 | yidong | 循环 | 1.17 | model/player/C_L7/mofamache/sm_L7_mofamache@yidong.FBX |
| 20870 | 保安树01 | idle | 循环 | 1.33 | model/player/C_L7/baoanshu01/L7_baoanshu_01_shenti@idle.FBX |
| 20871 | 保安树02 | idle | 循环 | 1.33 | model/player/C_L7/baoanshu02/L7_baoanshu_02@idle.FBX |
| 20871 | 保安树02 | run | 循环 | 0.73 | model/player/C_L7/baoanshu02/L7_baoanshu_02@run.FBX |
| 20871 | 保安树02 | walk | 循环 | 1.00 | model/player/C_L7/baoanshu02/L7_baoanshu_02@walk.FBX |
| 20872 | 保安树03 | idle | 循环 | 1.33 | model/player/C_L7/baoanshu03/L7_baoanshu_03@idle.FBX |
| 20872 | 保安树03 | walk | 循环 | 0.80 | model/player/C_L7/baoanshu03/L7_baoanshu_03@walk.FBX |
| 20873 | 保安树04 | idle | 循环 | 1.33 | model/player/C_L7/baoanshu04/L7_baoanshu_04@idle.FBX |
| 21061 | 无人机 | talk | 一次 | 3.73 | model/prop/WRJ/wurenji@talk.FBX |
| 21061 | 无人机 | Run | 循环 | 1.33 | model/prop/WRJ/wurenji@Run.FBX |
| 21061 | 无人机 | walk | 循环 | 1.33 | model/prop/WRJ/wurenji@Run.FBX |
| 21061 | 无人机 | run | 循环 | 1.33 | model/prop/WRJ/wurenji@Run.FBX |
| 21064 | 箭头 | Take 001 | 循环 | 2.00 | model/prop/WRJ/jintou_anim.FBX |
| 21281 | 巨大荷花 | heshang_idle | 循环 | 2.00 | model/player/C_L7/judahehua/L7_judahehua@heshang_idle.FBX |
| 21281 | 巨大荷花 | idle | 循环 | 2.00 | model/player/C_L7/judahehua/L7_judahehua@idle.FBX |
| 21390 | 神笔-笔杆（半成品）漂浮发光 | idle | 循环 | 2.00 | model/player/C_L9/qiankunshenbi/qiankunshenbi@idle.FBX |
| 21397 | 神器合集 | dakai | 一次 | 1.00 | model/player/C_L9/shenqiheji_shu/sm_L9_shenqiheji@dakai.FBX |
| 21397 | 神器合集 | dakai_idle | 循环 | 1.33 | model/player/C_L9/shenqiheji_shu/sm_L9_shenqiheji@dakai.FBX |
| 21397 | 神器合集 | idle | 循环 | 1.33 | model/player/C_L9/shenqiheji_shu/sm_L9_shenqiheji@idle.FBX |
| 21402 | 黑马人脑机接口 | run | 循环 | 0.53 | model/player/C_L9/marenpaobuji/marenpaobuji@run.FBX |
| 21402 | 黑马人脑机接口 | idle | 循环 | 1.60 | model/player/C_L9/marenpaobuji/marenpaobuji@idle.FBX |
| 21403 | 红马人脑机接口 | run | 循环 | 0.53 | model/player/C_L9/marenpaobuji/marenpaobuji@run.FBX |
| 21403 | 红马人脑机接口 | idle | 循环 | 1.60 | model/player/C_L9/marenpaobuji/marenpaobuji@idle.FBX |
| 21404 | 棕马人脑机接口 | run | 循环 | 0.53 | model/player/C_L9/marenpaobuji/marenpaobuji@run.FBX |
| 21404 | 棕马人脑机接口 | idle | 循环 | 1.60 | model/player/C_L9/marenpaobuji/marenpaobuji@idle.FBX |
| 21406 | 智能小车+厨艺箱 | idle | 循环 | 2.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle.FBX |
| 21406 | 智能小车+厨艺箱 | youzhuan_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan_guajian.FBX |
| 21406 | 智能小车+厨艺箱 | xianghou_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou_guajian.FBX |
| 21406 | 智能小车+厨艺箱 | xiangqian_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian_guajian.FBX |
| 21406 | 智能小车+厨艺箱 | xianghou | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou.FBX |
| 21406 | 智能小车+厨艺箱 | idle_guajian | 循环 | 1.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle_guajian.FBX |
| 21406 | 智能小车+厨艺箱 | zuozhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@zuozhuan.FBX |
| 21406 | 智能小车+厨艺箱 | xiangqian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian.FBX |
| 21406 | 智能小车+厨艺箱 | youzhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan.FBX |
| 21407 | 智能小车+魔法坩埚 | idle | 循环 | 2.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle.FBX |
| 21407 | 智能小车+魔法坩埚 | youzhuan_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan_guajian.FBX |
| 21407 | 智能小车+魔法坩埚 | xianghou_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou_guajian.FBX |
| 21407 | 智能小车+魔法坩埚 | xiangqian_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian_guajian.FBX |
| 21407 | 智能小车+魔法坩埚 | xianghou | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou.FBX |
| 21407 | 智能小车+魔法坩埚 | idle_guajian | 循环 | 1.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle_guajian.FBX |
| 21407 | 智能小车+魔法坩埚 | zuozhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@zuozhuan.FBX |
| 21407 | 智能小车+魔法坩埚 | xiangqian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian.FBX |
| 21407 | 智能小车+魔法坩埚 | youzhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan.FBX |
| 21574 | 龙宝宝3D精灵 | run | 循环 | 0.67 | model/player/C_L8/longbaobao/L8_longbaobao@run.FBX |
| 21574 | 龙宝宝3D精灵 | idle | 循环 | 1.33 | model/player/C_L8/longbaobao/L8_longbaobao@idle.FBX |
| 21574 | 龙宝宝3D精灵 | walk | 循环 | 0.93 | model/player/C_L8/longbaobao/L8_longbaobao@walk.FBX |
| 21753 | 智能小车魔药坩埚绿 | idle | 循环 | 2.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle.FBX |
| 21753 | 智能小车魔药坩埚绿 | youzhuan_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan_guajian.FBX |
| 21753 | 智能小车魔药坩埚绿 | xianghou_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou_guajian.FBX |
| 21753 | 智能小车魔药坩埚绿 | xiangqian_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian_guajian.FBX |
| 21753 | 智能小车魔药坩埚绿 | xianghou | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou.FBX |
| 21753 | 智能小车魔药坩埚绿 | idle_guajian | 循环 | 1.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle_guajian.FBX |
| 21753 | 智能小车魔药坩埚绿 | zuozhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@zuozhuan.FBX |
| 21753 | 智能小车魔药坩埚绿 | xiangqian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian.FBX |
| 21753 | 智能小车魔药坩埚绿 | youzhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan.FBX |
| 21998 | 围栏爬藤_精灵版 | idle | 循环 | 1.60 | model/player/C_L7/weilanpateng/L7_weilanpateng@idle.FBX |
| 22232 | 打招呼的信鸽 | idle | 循环 | 1.33 | model/player/C_L9/xinge/L9_xinge@idle.FBX |
| 22233 | 待机的信鸽 | feixing | 循环 | 0.83 | model/player/C_L9/xinge/L9_xinge@feixing.FBX |
| 22233 | 待机的信鸽 | idle | 循环 | 1.33 | model/player/C_L9/xinge/L9_xinge@idle.FBX |
| 22239 | 祈雨大炮_车轮 | run | 循环 | 1.33 | model/player/C_L9/qiyudapao/qiyudapao_chelun@run.fbx |
| 22240 | 飞行的信鸽 | feixing | 循环 | 0.83 | model/player/C_L9/xinge/L9_xinge@feixing.FBX |
| 22240 | 飞行的信鸽 | idle | 循环 | 1.33 | model/player/C_L9/xinge/L9_xinge@idle.FBX |
| 22246 | 椅子 | run | 循环 | 1.07 | model/player/C_L9/yizi/yizi@run.fbx |
| 22247 | 椅子01 | run | 循环 | 1.07 | model/player/C_L9/yizi/yizi@run.fbx |
| 22248 | 椅子02 | run | 循环 | 1.07 | model/player/C_L9/yizi/yizi@run.fbx |
| 22369 | 会飞的书 | idle | 循环 | 1.67 | model/player/C_L9/huifeideshu/sm_l9_hfds@idle.FBX |
| 22369 | 会飞的书 | dakai_loop | 循环 | 1.67 | model/player/C_L9/huifeideshu/sm_l9_hfds@dakai_loop.FBX |
| 22577 | 神笔-笔杆（半成品）漂浮 | idle | 循环 | 2.00 | model/player/C_L9/qiankunshenbi/qiankunshenbi@idle.FBX |
| 22590 | 漂浮 浮动的状态闪现花 | idle | 循环 | 1.67 | model/player/C_L9/shanxianhua/sm_L9_shanxianhua@idle.FBX |
| 22591 | 营地升级-增加武器库 | Take 001 | 循环 | 4.00 | model/C1/L7/Model/l7-04-01/sm_l7_yingdi_duanzao_01/sm_l7_yingdi_duanzao_01.FBX |
| 22601 | 待机2攻城车 | run_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run_wuwuqi.FBX |
| 22601 | 待机2攻城车 | idle | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle.FBX |
| 22601 | 待机2攻城车 | idle_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle_wuwuqi.FBX |
| 22601 | 待机2攻城车 | run | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run.FBX |
| 22602 | 神笔造墨锦囊 | idle | 循环 | 2.00 | model/player/C_L9/shenbizaomojinnang/shenbizaomojinnang@idle.FBX |
| 22614 | 攻城车毁损 | run_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run_wuwuqi.FBX |
| 22614 | 攻城车毁损 | idle | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle.FBX |
| 22614 | 攻城车毁损 | idle_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle_wuwuqi.FBX |
| 22614 | 攻城车毁损 | run | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run.FBX |
| 22623 | 行使1攻城车 | run_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run_wuwuqi.FBX |
| 22623 | 行使1攻城车 | idle | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle.FBX |
| 22623 | 行使1攻城车 | idle_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle_wuwuqi.FBX |
| 22623 | 行使1攻城车 | run | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run.FBX |
| 22624 | 攻击攻城车 | run_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run_wuwuqi.FBX |
| 22624 | 攻击攻城车 | idle | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle.FBX |
| 22624 | 攻击攻城车 | idle_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle_wuwuqi.FBX |
| 22624 | 攻击攻城车 | run | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run.FBX |
| 22625 | 行驶2攻城车 | run_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run_wuwuqi.FBX |
| 22625 | 行驶2攻城车 | idle | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle.FBX |
| 22625 | 行驶2攻城车 | idle_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle_wuwuqi.FBX |
| 22625 | 行驶2攻城车 | run | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run.FBX |
| 22626 | 待机1攻城车 | run_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run_wuwuqi.FBX |
| 22626 | 待机1攻城车 | idle | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle.FBX |
| 22626 | 待机1攻城车 | idle_wuwuqi | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@idle_wuwuqi.FBX |
| 22626 | 待机1攻城车 | run | 循环 | 2.00 | model/player/C_L9/gongchenghuoche/sm_L9_gongchenghuoche@run.FBX |
| 22765 | 监牢大门打开过程 | guanbi_loop | 一次 | 0.03 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX |
| 22765 | 监牢大门打开过程 | dakai_loop | 一次 | 0.03 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX |
| 22765 | 监牢大门打开过程 | dakai | 一次 | 1.30 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX |
| 22772 | 监牢大门关闭 | guanbi_loop | 一次 | 0.03 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX |
| 22772 | 监牢大门关闭 | dakai_loop | 一次 | 0.03 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX |
| 22772 | 监牢大门关闭 | dakai | 一次 | 1.30 | model/player/C_L9/sm_l9_jianlaodamen/sm_l9_jianlaodamen@anim.FBX |
| 23414 | 全向车_生命罗卜 | idle3 | 循环 | 1.33 | model/player/A1.1/quanxiangche_shengmingluobu/quanxiangche_shengmingluobu@idle3.FBX |
| 23414 | 全向车_生命罗卜 | idle to idle3 | 一次 | 1.00 | model/player/A1.1/quanxiangche_shengmingluobu/quanxiangche_shengmingluobu@idle3.FBX |
| 23414 | 全向车_生命罗卜 | idle to idle2 | 一次 | 2.00 | model/player/A1.1/quanxiangche_shengmingluobu/quanxiangche_shengmingluobu@idle2.FBX |
| 23414 | 全向车_生命罗卜 | idle | 循环 | 1.33 | model/player/A1.1/quanxiangche_shengmingluobu/quanxiangche_shengmingluobu@idle.FBX |
| 23414 | 全向车_生命罗卜 | idle2 | 循环 | 1.33 | model/player/A1.1/quanxiangche_shengmingluobu/quanxiangche_shengmingluobu@idle2.FBX |
| 23749 | 小精灵_3D精灵版 | idle | 循环 | 2.00 | model/player/C_L9/xiaojingling/L1_jingling@idle.FBX |
| 23751 | 鹦鹉草叉_3D精灵版 | huiwu | 循环 | 1.40 | model/player/C_L2/yingwucaocha/yingwucaocha@huiwu.FBX |
| 23751 | 鹦鹉草叉_3D精灵版 | beijifei | 循环 | 1.60 | model/player/C_L2/yingwucaocha/yingwucaocha@beijifei.fbx |
| 23753 | 小熊猫马桶撅_3D精灵版 | beidafei | 循环 | 1.33 | model/player/C_L2/xiaoxiongmaomatongjue/xxmmatongjue@beidafei.fbx |
| 23753 | 小熊猫马桶撅_3D精灵版 | matongjue | 循环 | 1.37 | model/player/C_L2/xiaoxiongmaomatongjue/xiaoxiongmao@matongjue.FBX |
| 23754 | 冷不丁_3D精灵版 | daolixingzou | 循环 | 0.80 | model/player/C_L7/lengbuding/L7_lengbuding@daolixingzou.FBX |
| 23754 | 冷不丁_3D精灵版 | yundao_loop | 循环 | 1.33 | model/player/C_L7/lengbuding/L7_lengbuding@yundao_loop.FBX |
| 23754 | 冷不丁_3D精灵版 | daolidaiji | 循环 | 1.60 | model/player/C_L7/lengbuding/L7_lengbuding@daolidaiji.FBX |
| 23754 | 冷不丁_3D精灵版 | walk | 循环 | 1.07 | model/player/C_L7/lengbuding/L7_lengbuding@walk.FBX |
| 23754 | 冷不丁_3D精灵版 | beidafei | 循环 | 1.60 | model/player/C_L7/lengbuding/L7_lengbuding@beidafei.fbx |
| 23754 | 冷不丁_3D精灵版 | xiadehoutuizuodishang_loop | 循环 | 1.33 | model/player/C_L7/lengbuding/L7_lengbuding@xiadehoutuizuodishang.FBX |
| 23754 | 冷不丁_3D精灵版 | xiadehoutuizuodishang_start | 一次 | 1.33 | model/player/C_L7/lengbuding/L7_lengbuding@xiadehoutuizuodishang.FBX |
| 23754 | 冷不丁_3D精灵版 | idle | 循环 | 1.60 | model/player/C_L7/lengbuding/L7_lengbuding@idle.FBX |
| 23754 | 冷不丁_3D精灵版 | run | 循环 | 0.67 | model/player/C_L7/lengbuding/L7_lengbuding@run.FBX |
| 23754 | 冷不丁_3D精灵版 | lache_loop | 循环 | 2.33 | model/player/C_L7/lengbuding/L7_lengbuding@lache_loop.FBX |
| 23754 | 冷不丁_3D精灵版 | xiadehoutuizuodishang_end | 一次 | 1.20 | model/player/C_L7/lengbuding/L7_lengbuding@xiadehoutuizuodishang.FBX |
| 23794 | 卡皮巴拉士兵06_3D精灵版 | idle | 循环 | 2.00 | model/player/C_L5/kapibalashibing06/kapibalashibing06@idle.FBX |
| 23794 | 卡皮巴拉士兵06_3D精灵版 | walk | 循环 | 1.20 | model/player/C_L5/kapibalashibing06/kapibalashibing06@walk.FBX |
| 23794 | 卡皮巴拉士兵06_3D精灵版 | attack | 循环 | 1.90 | model/player/C_L5/kapibalashibing06/kapibalashibing06@attack.FBX |
| 23795 | 粉红河马_3D精灵版 | idle | 循环 | 2.00 | model/player/C_L3/fenhonghema_chengnian/fenhonghema@idle.FBX |
| 23795 | 粉红河马_3D精灵版 | run | 循环 | 0.60 | model/player/C_L3/fenhonghema_chengnian/fenhonghema@run.fbx |
| 23795 | 粉红河马_3D精灵版 | fly | 循环 | 0.67 | model/player/C_L3/fenhonghema_chengnian/fenhonghema@fly.fbx |
| 23795 | 粉红河马_3D精灵版 | walk | 循环 | 0.97 | model/player/C_L3/fenhonghema_chengnian/fenhonghema@walk.fbx |
| 23797 | 土拨鼠长老红_3D精灵版 | run | 循环 | 0.93 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@run.FBX |
| 23797 | 土拨鼠长老红_3D精灵版 | idle | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@idle.FBX |
| 23797 | 土拨鼠长老红_3D精灵版 | daodi | 一次 | 0.93 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@daodi.FBX |
| 23797 | 土拨鼠长老红_3D精灵版 | daodi_idle | 循环 | 2.17 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@daodi.FBX |
| 23797 | 土拨鼠长老红_3D精灵版 | walk | 循环 | 1.13 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@walk.FBX |
| 23797 | 土拨鼠长老红_3D精灵版 | dichuguaizhang_idle | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao_red@dichuguaizhang_idle.fbx |
| 23797 | 土拨鼠长老红_3D精灵版 | beidafei | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao_red@beidafei.fbx |
| 23798 | 土拨鼠长老绿_3D精灵版 | beidafei | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao_red@beidafei.fbx |
| 23798 | 土拨鼠长老绿_3D精灵版 | run | 循环 | 0.93 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@run.FBX |
| 23798 | 土拨鼠长老绿_3D精灵版 | idle | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@idle.FBX |
| 23798 | 土拨鼠长老绿_3D精灵版 | dichuguaizhang_idle | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao_red@dichuguaizhang_idle.fbx |
| 23798 | 土拨鼠长老绿_3D精灵版 | daodi | 一次 | 0.93 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@daodi.FBX |
| 23798 | 土拨鼠长老绿_3D精灵版 | daodi_idle | 循环 | 2.17 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@daodi.FBX |
| 23798 | 土拨鼠长老绿_3D精灵版 | walk | 循环 | 1.13 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@walk.FBX |
| 23799 | 土拨鼠长老蓝_3D精灵版 | dichuguaizhang_idle | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao_red@dichuguaizhang_idle.fbx |
| 23799 | 土拨鼠长老蓝_3D精灵版 | run | 循环 | 0.93 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@run.FBX |
| 23799 | 土拨鼠长老蓝_3D精灵版 | idle | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@idle.FBX |
| 23799 | 土拨鼠长老蓝_3D精灵版 | daodi | 一次 | 0.93 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@daodi.FBX |
| 23799 | 土拨鼠长老蓝_3D精灵版 | daodi_idle | 循环 | 2.17 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@daodi.FBX |
| 23799 | 土拨鼠长老蓝_3D精灵版 | walk | 循环 | 1.13 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao@walk.FBX |
| 23799 | 土拨鼠长老蓝_3D精灵版 | beidafei | 循环 | 1.60 | model/player/C_L4/tuboshuzhanglao/tuboshuzhanglao_red@beidafei.fbx |
| 23909 | 火烈鸟棒子（欧阳版） | idle | 循环 | 1.33 | model/player/C_L10/huolieniao_bangzi/L10_huolieniao_bangzi@idle.FBX |
| 23930 | 玫瑰花 | piao_idle | 循环 | 2.00 | model/player/C_L10/meiguihua/sm_l10_meiguihua@piao_idle.FBX |
| 23931 | 倒计时玫瑰花 | kuwei_idle | 循环 | 2.00 | model/player/C_L10/meiguihua_daojishi/sm_l10_meiguihua_daojishi@kuwei_idle.FBX |
| 23931 | 倒计时玫瑰花 | piao_idle | 循环 | 2.00 | model/player/C_L10/meiguihua_daojishi/sm_l10_meiguihua_daojishi@piao_idle.FBX |
| 23944 | 棒打柠檬药水满杯 | anim | 循环 | 1.60 | model/player/C_L10/ningmengyaoshui/sm_nmys@anim.fbx |
| 23967 | 大礼帽3D精灵版 | feixing | 循环 | 0.80 | model/player/C_L10/dalimao/dalimao@feixing.fbx |
| 23967 | 大礼帽3D精灵版 | idle | 循环 | 1.33 | model/player/C_L10/dalimao/dalimao@idle.fbx |
| 23970 | 疯帽匠+大礼帽 | anim | 循环 | 1.87 | model/player/C_L10/fengmaojiang+dalimao/fengmaojiang+dalimao@anim.FBX |
| 24137 | 疯帽匠3D精灵版 | jifei_loop | 循环 | 1.33 | model/player/C_L10/fengmaojiang/L10_fengmaojiang@jifei_loop.FBX |
| 24137 | 疯帽匠3D精灵版 | run | 循环 | 0.67 | model/player/C_L10/fengmaojiang/L10_fengmaojiang@run.FBX |
| 24137 | 疯帽匠3D精灵版 | idle | 循环 | 1.60 | model/player/C_L10/fengmaojiang/L10_fengmaojiang@idle.FBX |
| 24137 | 疯帽匠3D精灵版 | walk | 循环 | 1.07 | model/player/C_L10/fengmaojiang/L10_fengmaojiang@walk.FBX |
| 24155 | 老毛虫 | qiyun_loop | 循环 | 1.53 | model/player/C_L10/laomaochong/L10_laomaochong@qiyun_loop.fbx |
| 24155 | 老毛虫 | idle | 循环 | 1.60 | model/player/C_L10/laomaochong/L10_laomaochong@idle.fbx |
| 24173 | 快问快答卷 | anim | 循环 | 1.60 | model/player/C_L10/kwkdj+pyxxj/kwkdj@anim.fbx |
| 24174 | 朋友肖像卷 | anim | 循环 | 1.60 | model/player/C_L10/kwkdj+pyxxj/xxj@anim.fbx |
| 24175 | 茧 | niudong | 一次 | 2.27 | model/player/C_L10/jian/jian@niudong.fbx |
| 24175 | 茧 | idle | 循环 | 0.03 | model/player/C_L10/jian/jian@niudong.fbx |
| 24184 | 茶壶女茶杯男 | idle | 循环 | 1.00 | model/player/C_L10/chahunv+chabeinan/chahuchuniang@idle.fbx |
| 24198 | 黄色咖啡杯带动画 | bengtiao | 循环 | 1.00 | model/player/C_L10/chabei/chabei@anim.fbx |
| 24198 | 黄色咖啡杯带动画 | idle | 循环 | 1.33 | model/player/C_L10/chabei/chabei@anim.fbx |
| 24199 | 绿色咖啡杯带动画 | bengtiao | 循环 | 1.00 | model/player/C_L10/chabei/chabei@anim.fbx |
| 24199 | 绿色咖啡杯带动画 | idle | 循环 | 1.33 | model/player/C_L10/chabei/chabei@anim.fbx |
| 24344 | 蓝色茶壶动画版 | bengtiao | 循环 | 0.67 | model/player/C_L10/chahu/sm_l10_chhcz_chahu04@bengtiao.FBX |
| 24344 | 蓝色茶壶动画版 | idle | 循环 | 1.60 | model/player/C_L10/chahu/sm_l10_chhcz_chahu04@idle.FBX |
| 24345 | 棕色茶壶动画版 | bengtiao | 循环 | 0.67 | model/player/C_L10/chahu/sm_l10_chhcz_chahu03@bengtiao.FBX |
| 24345 | 棕色茶壶动画版 | idle | 循环 | 1.60 | model/player/C_L10/chahu/sm_l10_chhcz_chahu03@idle.FBX |
| 24346 | 粉丝茶壶动画版 | bengtiao | 循环 | 0.60 | model/player/C_L10/chahu/sm_l10_chhczfenchahu@bengtiao.fbx |
| 24346 | 粉丝茶壶动画版 | idle | 循环 | 1.67 | model/player/C_L10/chahu/sm_l10_chhczfenchahu@idle.fbx |
| 24347 | 紫色茶壶动画版 | idle | 循环 | 1.67 | model/player/C_L10/chahu/sm_l10_chhczzisechahu@idle.fbx |
| 24347 | 紫色茶壶动画版 | bengtiao | 循环 | 0.60 | model/player/C_L10/chahu/sm_l10_chhczzisechahu@bengtiao.fbx |
| 24400 | 百灵扫帚女童 | saohui | 一次 | 3.33 | model/player/C_L10/bailingsaozhounvtong/sm_l10_saozhounvtong_bailingbanben@saohui.FBX |
| 24400 | 百灵扫帚女童 | idle | 循环 | 1.60 | model/player/C_L10/bailingsaozhounvtong/sm_l10_saozhounvtong_bailingbanben@idle.FBX |
| 25080 | 贝壳珍珠 | idle | 循环 | 2.00 | model/player/C_L11/beikezhenzhu/beikezhenzhu@anim.fbx |
| 25080 | 贝壳珍珠 | dakai | 一次 | 3.33 | model/player/C_L11/beikezhenzhu/beikezhenzhu@anim.fbx |
| 25479 | 寻龙分金尺 | luanzhuan | 一次 | 2.17 | model/player/C_L11/fenjinchi/sm_l11_fenjinchi@luanzhuan.fbx |
| 25480 | 千面神灯 | idle | 循环 | 1.33 | model/player/C_L11/qianmianshendeng/sm_l11_qmsd@idle.fbx |
| 25609 | 社牛水晶球_带动画 | idle | 循环 | 1.33 | model/player/C_L11/sheniushuijingqiu/sm_l10_sheniushuijingqiu@idle.FBX |
| 25609 | 社牛水晶球_带动画 | walk | 循环 | 1.33 | model/player/C_L11/sheniushuijingqiu/sm_l10_sheniushuijingqiu@walk.FBX |
| 25850 | 水晶圈 | piao_idle | 循环 | 2.00 | model/player/C_L11/shuijingquan/sm_l11_shuijinquan@piao_idle.fbx |
| 25852 | 智能小车混沌星核 | idle | 循环 | 2.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle.FBX |
| 25852 | 智能小车混沌星核 | youzhuan_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan_guajian.FBX |
| 25852 | 智能小车混沌星核 | xianghou_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou_guajian.FBX |
| 25852 | 智能小车混沌星核 | xiangqian_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian_guajian.FBX |
| 25852 | 智能小车混沌星核 | xianghou | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou.FBX |
| 25852 | 智能小车混沌星核 | idle_guajian | 循环 | 1.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle_guajian.FBX |
| 25852 | 智能小车混沌星核 | zuozhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@zuozhuan.FBX |
| 25852 | 智能小车混沌星核 | xiangqian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian.FBX |
| 25852 | 智能小车混沌星核 | youzhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan.FBX |
| 25853 | 招财猫 | idle | 循环 | 1.73 | model/player/C_L11/zhaocaimao/sm_l11_zhaocaimao@idle.fbx |
| 26567 | 希斯发3D精灵 | fangyu_loop | 循环 | 1.20 | model/player/C_L11/xisifa/L11_xisifa@fangyu.fbx |
| 26567 | 希斯发3D精灵 | kongzhong_loop | 循环 | 2.00 | model/player/C_L11/xisifa/L11_xisifa@kongzhong.fbx |
| 26567 | 希斯发3D精灵 | fangyu | 一次 | 0.63 | model/player/C_L11/xisifa/L11_xisifa@fangyu.fbx |
| 26567 | 希斯发3D精灵 | walk | 循环 | 1.20 | model/player/C_L11/xisifa/L11_xisifa@walk.FBX |
| 26567 | 希斯发3D精灵 | kongzhong_start | 一次 | 1.90 | model/player/C_L11/xisifa/L11_xisifa@kongzhong.fbx |
| 26567 | 希斯发3D精灵 | idle | 循环 | 1.60 | model/player/C_L11/xisifa/L11_xisifa@idle.FBX |
| 26567 | 希斯发3D精灵 | kongzhong_end | 一次 | 0.90 | model/player/C_L11/xisifa/L11_xisifa@kongzhong.fbx |
| 26567 | 希斯发3D精灵 | run | 循环 | 0.67 | model/player/C_L11/xisifa/L11_xisifa@run.FBX |
| 26567 | 希斯发3D精灵 | yundaozaidi | 循环 | 1.87 | model/player/C_L11/xisifa/L11_xisifa@yundaozaidi.fbx |
| 26567 | 希斯发3D精灵 | fukong idle | 循环 | 1.60 | model/player/C_L11/xisifa/L11_xisifa@fukong idle.FBX |
| 26692 | 特斯拉时空跑车崭新版 | idle | 循环 | 1.00 | model/player/C_L12/sm_l12_paoche/sm_l12_paoche@idle.fbx |
| 26692 | 特斯拉时空跑车崭新版 | run | 循环 | 2.00 | model/player/C_L12/sm_l12_paoche/sm_l12_paoche@run.fbx |
| 26693 | 特斯拉时空跑车灰尘版 | idle | 循环 | 1.00 | model/player/C_L12/sm_l12_paoche/sm_l12_paoche@idle.fbx |
| 26693 | 特斯拉时空跑车灰尘版 | run | 循环 | 2.00 | model/player/C_L12/sm_l12_paoche/sm_l12_paoche@run.fbx |
| 26918 | 希斯发未黑化3D精灵版 | run | 循环 | 0.67 | model/player/C_L11/xisifa/L11_xisifa@run.FBX |
| 26918 | 希斯发未黑化3D精灵版 | zhanbai | 循环 | 1.87 | model/player/C_L12/xisifa_weiheihua/L11_xisifa@zhanbai.fbx |
| 26918 | 希斯发未黑化3D精灵版 | walk | 循环 | 1.07 | model/player/C_L12/xisifa_weiheihua/L11_xisifa@walk.FBX |
| 26918 | 希斯发未黑化3D精灵版 | idle | 循环 | 1.60 | model/player/C_L12/xisifa_weiheihua/L11_xisifa@idle.FBX |
| 27068 | 机械臂全向车 | run | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche/jixiebiquanxiangche@run.fbx |
| 27068 | 机械臂全向车 | idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche/jixiebiquanxiangche@idle.fbx |
| 27068 | 机械臂全向车 | run_taichazi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche/jixiebiquanxiangche@run_taichazi.fbx |
| 27068 | 机械臂全向车 | idle_taichazi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche/jixiebiquanxiangche@idle_taichazi.fbx |
| 27083 | 特斯拉时空跑车发光 | idle | 循环 | 1.00 | model/player/C_L12/sm_l12_paoche/sm_l12_paoche@idle.fbx |
| 27083 | 特斯拉时空跑车发光 | run | 循环 | 2.00 | model/player/C_L12/sm_l12_paoche/sm_l12_paoche@run.fbx |
| 27239 | 机械臂全向车 | houtui | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@houtui.fbx |
| 27239 | 机械臂全向车 | run | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run.fbx |
| 27239 | 机械臂全向车 | shenjiazhuadaiji | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua.fbx |
| 27239 | 机械臂全向车 | idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle.fbx |
| 27239 | 机械臂全向车 | shenjiazhua | 一次 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua.fbx |
| 27239 | 机械臂全向车 | shenjiazhua02 | 一次 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua02.fbx |
| 27239 | 机械臂全向车 | shenjiazhua02_idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua02.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | idle_jiaqi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle_jiaqi.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | fangxia | 一次 | 3.00 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@jiaqi.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | run_qubijiaqi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run_qubijiaqi.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | jiaxiangzi | 一次 | 1.67 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@jiaqi 1.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | idle_jiaxiangzi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle_jiaxiangzi.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | jiaqi | 一次 | 3.00 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@jiaqi.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | run_jiaqi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run_jiaqi.fbx |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | run_qubijiaqi02 | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run_qubijiaqi02.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | idle_jiaqi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle_jiaqi.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | fangxia | 一次 | 3.00 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@jiaqi.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | run_qubijiaqi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run_qubijiaqi.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | jiaxiangzi | 一次 | 1.67 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@jiaqi 1.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | idle_jiaxiangzi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle_jiaxiangzi.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | jiaqi | 一次 | 3.00 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@jiaqi.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | run_jiaqi | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run_jiaqi.fbx |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | run_qubijiaqi02 | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run_qubijiaqi02.fbx |
| 27392 | 曼德拉草3D精灵 | dishang_idle | 循环 | 1.33 | model/player/C_L7/mandelacao/L7_mandelacao@dishang_idle.FBX |
| 27392 | 曼德拉草3D精灵 | dixia_idle | 循环 | 1.33 | model/player/C_L7/mandelacao/L7_mandelacao@dixia_idle.FBX |
| 27393 | 矮人3D精灵 | idle | 循环 | 1.60 | model/player/C_L9/airen/L9_airen@idle.FBX |
| 27393 | 矮人3D精灵 | walk | 循环 | 1.47 | model/player/C_L9/airen/L9_airen@walk.FBX |
| 27393 | 矮人3D精灵 | run | 循环 | 1.00 | model/player/C_L9/airen/L9_airen@run.FBX |
| 27393 | 矮人3D精灵 | zuozhewan | 循环 | 5.13 | model/player/C_L9/airen/L9_airen@zuozhewan.FBX |
| 27534 | 机械臂全向车装满草 | houtui | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@houtui.fbx |
| 27534 | 机械臂全向车装满草 | run | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run.fbx |
| 27534 | 机械臂全向车装满草 | shenjiazhuadaiji | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua.fbx |
| 27534 | 机械臂全向车装满草 | idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle.fbx |
| 27534 | 机械臂全向车装满草 | shenjiazhua | 一次 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua.fbx |
| 27534 | 机械臂全向车装满草 | shenjiazhua02 | 一次 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua02.fbx |
| 27534 | 机械臂全向车装满草 | shenjiazhua02_idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua02.fbx |
| 27549 | 机械臂全向车装货框版 | houtui | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@houtui.fbx |
| 27549 | 机械臂全向车装货框版 | run | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@run.fbx |
| 27549 | 机械臂全向车装货框版 | shenjiazhuadaiji | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua.fbx |
| 27549 | 机械臂全向车装货框版 | idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@idle.fbx |
| 27549 | 机械臂全向车装货框版 | shenjiazhua | 一次 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua.fbx |
| 27549 | 机械臂全向车装货框版 | shenjiazhua02 | 一次 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua02.fbx |
| 27549 | 机械臂全向车装货框版 | shenjiazhua02_idle | 循环 | 1.33 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@shenjiazhua02.fbx |
| 27551 | 队长魔法袍03_3D精灵 | beibang | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@beibang.FBX |
| 27551 | 队长魔法袍03_3D精灵 | jingyataitou | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@jingyataitou.FBX |
| 27551 | 队长魔法袍03_3D精灵 | daoli_idle | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@daoli_idle.FBX |
| 27551 | 队长魔法袍03_3D精灵 | walk | 循环 | 1.07 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@walk.FBX |
| 27551 | 队长魔法袍03_3D精灵 | idle | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@idle.FBX |
| 27551 | 队长魔法袍03_3D精灵 | guizhuo_idle | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@guizhuo_idle.fbx |
| 27551 | 队长魔法袍03_3D精灵 | daoli_run | 循环 | 0.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@daoli_run.FBX |
| 27551 | 队长魔法袍03_3D精灵 | huidaiji | 一次 | 1.60 | model/player/C_L7/duizhangmofapao/duizhangmofapao_longdi@anim.FBX |
| 27551 | 队长魔法袍03_3D精灵 | qitiao_end | 一次 | 1.27 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@qitiao.fbx |
| 27551 | 队长魔法袍03_3D精灵 | nalongdi_idle | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/duizhangmofapao_longdi@anim.FBX |
| 27551 | 队长魔法袍03_3D精灵 | run | 循环 | 0.67 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@run.FBX |
| 27551 | 队长魔法袍03_3D精灵 | qitiao_loop | 循环 | 1.50 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@qitiao.fbx |
| 27551 | 队长魔法袍03_3D精灵 | mofabang_idle | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@mofabang_idle.FBX |
| 27551 | 队长魔法袍03_3D精灵 | qitiao_start | 一次 | 1.10 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@qitiao.fbx |
| 27551 | 队长魔法袍03_3D精灵 | sichuzhangwangzou | 循环 | 2.13 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@sichuzhangwangzou.FBX |
| 27551 | 队长魔法袍03_3D精灵 | chuilongdi_loop | 循环 | 1.33 | model/player/C_L7/duizhangmofapao/duizhangmofapao_longdi@anim.FBX |
| 27551 | 队长魔法袍03_3D精灵 | yundao_shuizhao | 循环 | 1.33 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@yundao_shuizhao.fbx |
| 27551 | 队长魔法袍03_3D精灵 | danshoubeng | 循环 | 2.27 | model/player/C_L7/duizhangmofapao/L7_duizhangmofapao@danshoubeng.FBX |
| 27551 | 队长魔法袍03_3D精灵 | chuilongdi | 一次 | 0.73 | model/player/C_L7/duizhangmofapao/duizhangmofapao_longdi@anim.FBX |
| 27551 | 队长魔法袍03_3D精灵 | nachulongdi | 一次 | 0.73 | model/player/C_L7/duizhangmofapao/duizhangmofapao_longdi@anim.FBX |
| 27551 | 队长魔法袍03_3D精灵 | najianju_idle | 循环 | 1.60 | model/player/C_L7/duizhangmofapao/L8_duizhangmofapaoshengji02@najianju_idle.fbx |
| 27552 | 雪球0_5_3D精灵 | shizhong | 一次 | 2.97 | model/player/C_L2/xueqiuL0_5/L1_xueqiuL0_5@shizhong.fbx |
| 27552 | 雪球0_5_3D精灵 | idle | 循环 | 1.60 | model/player/C_L2/xueqiuL0_5/xueqiuL0_5@idle.FBX |
| 27552 | 雪球0_5_3D精灵 | piaofu | 循环 | 1.33 | model/player/C_L2/xueqiuL0_5/L1_xueqiuL0_5@shizhong.fbx |
| 27552 | 雪球0_5_3D精灵 | danxin | 循环 | 1.60 | model/player/C_L2/xueqiuL0_5/xueqiuL0_5@danxin.fbx |
| 27552 | 雪球0_5_3D精灵 | aojiao | 循环 | 2.53 | model/player/C_L2/xueqiuL0_5/xueqiuL0_5@aojiao.FBX |
| 27552 | 雪球0_5_3D精灵 | walk | 循环 | 1.20 | model/player/C_L2/xueqiuL0_5/xueqiuL0_5@walk.FBX |
| 27552 | 雪球0_5_3D精灵 | run | 循环 | 0.47 | model/player/C_L2/xueqiuL0_5/xueqiuL0_5@run.FBX |
| 27553 | 桃子魔法袍_3D精灵 | nawuqi_idle | 循环 | 1.60 | model/player/C_L7/taozimofapao/L7_taozimofapao@nawuqi_idle.FBX |
| 27553 | 桃子魔法袍_3D精灵 | shifangmofa | 一次 | 2.57 | model/player/C_L7/taozimofapao/L7_taozimofapao@shifangmofa.FBX |
| 27553 | 桃子魔法袍_3D精灵 | run | 循环 | 0.67 | model/player/C_L7/taozimofapao/L7_taozimofapao@run.FBX |
| 27553 | 桃子魔法袍_3D精灵 | idle | 循环 | 1.60 | model/player/C_L7/taozimofapao/L7_taozimofapao@idle.FBX |
| 27553 | 桃子魔法袍_3D精灵 | walk | 循环 | 1.07 | model/player/C_L7/taozimofapao/L7_taozimofapao@walk.FBX |
| 27554 | 乌拉乎魔法袍_3D精灵 | mofabang_idle | 循环 | 1.87 | model/player/C_L7/wulahumofapao/wulahumofapao@mofabang_idle.FBX |
| 27554 | 乌拉乎魔法袍_3D精灵 | huangzhangpao | 循环 | 0.47 | model/player/C_L7/wulahumofapao/wulahumofapao@huangzhangpao.FBX |
| 27554 | 乌拉乎魔法袍_3D精灵 | run | 循环 | 0.73 | model/player/C_L7/wulahumofapao/wulahumofapao@run.FBX |
| 27554 | 乌拉乎魔法袍_3D精灵 | beileijizhongxuanyun | 循环 | 1.67 | model/player/C_L7/wulahumofapao/L7_wulahumofapao@beileijizhongxuanyun.FBX |
| 27554 | 乌拉乎魔法袍_3D精灵 | idle | 循环 | 1.87 | model/player/C_L7/wulahumofapao/wulahumofapao@idle.FBX |
| 27554 | 乌拉乎魔法袍_3D精灵 | walk | 循环 | 1.07 | model/player/C_L7/wulahumofapao/wulahumofapao@walk.FBX |
| 27555 | 禾木魔法袍_3D精灵 | walk | 循环 | 1.07 | model/player/C_L7/hemumofapao/hemumofapao@walk.FBX |
| 27555 | 禾木魔法袍_3D精灵 | yundaozaidi | 循环 | 1.37 | model/player/C_L7/hemumofapao/hemumofapao@yundaozaidi.fbx |
| 27555 | 禾木魔法袍_3D精灵 | idle | 循环 | 1.37 | model/player/C_L7/hemumofapao/hemumofapao@idle.FBX |
| 27555 | 禾木魔法袍_3D精灵 | run | 循环 | 0.67 | model/player/C_L7/hemumofapao/hemumofapao@run.FBX |
| 27956 | 智能小车混沌星核无超声传感 | idle | 循环 | 2.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle.FBX |
| 27956 | 智能小车混沌星核无超声传感 | youzhuan_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan_guajian.FBX |
| 27956 | 智能小车混沌星核无超声传感 | xianghou_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou_guajian.FBX |
| 27956 | 智能小车混沌星核无超声传感 | xiangqian_guajian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian_guajian.FBX |
| 27956 | 智能小车混沌星核无超声传感 | xianghou | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xianghou.FBX |
| 27956 | 智能小车混沌星核无超声传感 | idle_guajian | 循环 | 1.00 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@idle_guajian.FBX |
| 27956 | 智能小车混沌星核无超声传感 | zuozhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@zuozhuan.FBX |
| 27956 | 智能小车混沌星核无超声传感 | xiangqian | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@xiangqian.FBX |
| 27956 | 智能小车混沌星核无超声传感 | youzhuan | 循环 | 1.07 | model/player/C_L7/zhinengxiaoche/sm_l7_zhinengxiaoche@youzhuan.FBX |
| 28055 | 雷达 | leidachuxian | 一次 | 1.17 | model/player/C_L2/maoleida/maoleida@leidachuxian.FBX |
| 28055 | 雷达 | leidadaiji | 一次 | 1.00 | model/player/C_L2/maoleida/maoleida@leidadaiji.FBX |
| 28055 | 雷达 | idle | 循环 | 0.56 | model/player/C_L2/maoleida/maoleida@idle.FBX |
| 28070 | 无人机 | walk | 循环 | 1.33 | model/player/C_L13/wurenji/L13_wurenji@anim.fbx |
| 28070 | 无人机 | idle | 循环 | 1.33 | model/player/C_L13/wurenji/L13_wurenji@anim.fbx |
| 28070 | 无人机 | run | 循环 | 1.33 | model/player/C_L13/wurenji/L13_wurenji@anim.fbx |
| 28070 | 无人机 | fiy | 循环 | 1.33 | model/player/C_L13/wurenji/L13_wurenji@anim.fbx |
| 28106 | 物资箱带动画 | dakai_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@dakai_idle.fbx |
| 28106 | 物资箱带动画 | bihe_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@bihe_idle.fbx |
| 28107 | 风车 | Take 001 | 循环 | 2.00 | model/C1/L6/Model/l6_03_01/fengche/fengche01_anim.FBX |
| 28108 | 魔药园风车建筑 | Take 001 | 循环 | 2.00 | model/C1/L7/Model/l7-02-02/sm_l7_myy_fengche/sm_l7_myy_fengche.FBX |
| 28264 | 物资箱带动画02 | dakai_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@dakai_idle.fbx |
| 28264 | 物资箱带动画02 | bihe_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@bihe_idle.fbx |
| 28273 | 雷达带动画 | jiance | 循环 | 2.00 | model/player/C_L14/leida_anim/sm_l13_leida.fbx |
| 28364 | 物资库大门 | dakai | 一次 | 2.30 | model/player/C_L14/wuzikudamen/wuzikudamen@anim.fbx |
| 28364 | 物资库大门 | kai | 一次 | 0.03 | model/player/C_L14/wuzikudamen/wuzikudamen@anim.fbx |
| 28364 | 物资库大门 | guan | 一次 | 0.03 | model/player/C_L14/wuzikudamen/wuzikudamen@anim.fbx |
| 28679 | 矿洞大门 | kai | 一次 | 0.03 | model/player/C_L14/kuangdongdamen/kuangdongdamen.fbx |
| 28679 | 矿洞大门 | kaimen | 一次 | 3.33 | model/player/C_L14/kuangdongdamen/kuangdongdamen.fbx |
| 28679 | 矿洞大门 | guan | 一次 | 0.03 | model/player/C_L14/kuangdongdamen/kuangdongdamen.fbx |
| 28999 | 全向车机械臂货框颜色传感器 | kaijiazhua | 一次 | 1.00 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@kaijiazhua.fbx |
| 28999 | 全向车机械臂货框颜色传感器 | guanbijiazhua | 一次 | 2.00 | model/player/C_L7/jixiebiquanxiangche_jiexiebi/jixiebiquanxiangche_jixiebi@kaijiazhua.fbx |
| 29009 | 降维陨石碎片 | idle | 循环 | 2.00 | model/player/C_L13/jiangweiyunshisuipian/jiangweiyunshisuipian@idle.fbx |
| 29111 | 脑电波机 | idle | 循环 | 2.00 | model/player/C_L14/hemunaodianboji/hemunaodianboji@idle.fbx |
| 29157 | 窑炉口 | penqi | 一次 | 2.00 | model/player/C_L14/yaolukou/sm_l15_fenleijiqi@anim.fbx |
| 29157 | 窑炉口 | idle | 一次 | 0.03 | model/player/C_L14/yaolukou/sm_l15_fenleijiqi@anim.fbx |
| 29243 | 分割机器 | idle | 一次 | 0.03 | model/player/C_L14/fengejiqi/fengejiqi@anim.fbx |
| 29243 | 分割机器 | penqi | 一次 | 2.00 | model/player/C_L14/fengejiqi/fengejiqi@anim.fbx |
| 29265 | 盲盒 | idle | 一次 | 0.03 | model/player/C_L14/manghe/manghe@anim.fbx |
| 29265 | 盲盒 | dakai | 一次 | 0.67 | model/player/C_L14/manghe/manghe@anim.fbx |
| 29265 | 盲盒 | dakai_loop | 一次 | 0.03 | model/player/C_L14/manghe/manghe@anim.fbx |
| 29290 | 食物箱 | dakai_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@dakai_idle.fbx |
| 29290 | 食物箱 | bihe_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@bihe_idle.fbx |
| 29297 | 漫波神庙大门 | dakai | 一次 | 2.33 | model/player/C_L14/manboshenmiaodamen/manboshenmiaodamen@anim.fbx |
| 29297 | 漫波神庙大门 | dakai_loop | 一次 | 0.03 | model/player/C_L14/manboshenmiaodamen/manboshenmiaodamen@anim.fbx |
| 29297 | 漫波神庙大门 | guanbi | 一次 | 0.03 | model/player/C_L14/manboshenmiaodamen/manboshenmiaodamen@anim.fbx |
| 29298 | 漫波大神庙密码门 | guanbi | 一次 | 0.03 | model/player/C_L14/manboshenmiao_mimamen/mbsd_mimamen@anim.fbx |
| 29298 | 漫波大神庙密码门 | dakai | 一次 | 1.37 | model/player/C_L14/manboshenmiao_mimamen/mbsd_mimamen@anim.fbx |
| 29298 | 漫波大神庙密码门 | dakai_loop | 一次 | 0.03 | model/player/C_L14/manboshenmiao_mimamen/mbsd_mimamen@anim.fbx |
| 29299 | 切割机器 | dakai | 一次 | 1.63 | model/player/C_L14/qiegejiqi/14_qgjq@anim.fbx |
| 29299 | 切割机器 | guanbi | 一次 | 0.03 | model/player/C_L14/qiegejiqi/14_qgjq@anim.fbx |
| 29299 | 切割机器 | dakai_loop | 循环 | 0.67 | model/player/C_L14/qiegejiqi/14_qgjq@anim.fbx |
| 29334 | 钟表 | 6dian | 一次 | 0.03 | model/player/C_L14/zhongbiao/zhongbiao@anim.fbx |
| 29334 | 钟表 | 10dian | 一次 | 0.03 | model/player/C_L14/zhongbiao/zhongbiao@anim.fbx |
| 29334 | 钟表 | zhuan | 一次 | 2.00 | model/player/C_L14/zhongbiao/zhongbiao@anim.fbx |
| 29633 | 马车 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29633 | 马车 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29637 | 榴莲 | dakai | 一次 | 1.00 | model/player/C_L14/liulian/liulian@skin.fbx |
| 29637 | 榴莲 | dakai_loop | 一次 | 0.03 | model/player/C_L14/liulian/liulian@skin.fbx |
| 29637 | 榴莲 | bihe | 一次 | 0.03 | model/player/C_L14/liulian/liulian@skin.fbx |
| 29638 | 榴莲坏了 | dakai | 一次 | 1.00 | model/player/C_L14/liulian/liulian@skin.fbx |
| 29638 | 榴莲坏了 | dakai_loop | 一次 | 0.03 | model/player/C_L14/liulian/liulian@skin.fbx |
| 29638 | 榴莲坏了 | bihe | 一次 | 0.03 | model/player/C_L14/liulian/liulian@skin.fbx |
| 29661 | 曼德拉草_捕狼草 | dishang_idle | 循环 | 1.33 | model/player/C_L7/mandelacao/L7_mandelacao@dishang_idle.FBX |
| 29661 | 曼德拉草_捕狼草 | dixia_idle | 循环 | 1.33 | model/player/C_L7/mandelacao/L7_mandelacao@dixia_idle.FBX |
| 29663 | 商人货车白 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29663 | 商人货车白 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29664 | 商人货车黑 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29664 | 商人货车黑 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29675 | 护卫机甲 | walk | 循环 | 1.53 | model/player/C_L9/mofarenou/L9_mofarenou1@walk.FBX |
| 29675 | 护卫机甲 | idle | 循环 | 1.60 | model/player/C_L9/mofarenou/L9_mofarenou1@idle.FBX |
| 29675 | 护卫机甲 | run | 循环 | 1.13 | model/player/C_L9/mofarenou/L9_mofarenou1@run.FBX |
| 29804 | 马车黄色无货物 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29804 | 马车黄色无货物 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29805 | 马车黄色有货物 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29805 | 马车黄色有货物 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29806 | 马车白色无货物 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29806 | 马车白色无货物 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29807 | 马车白色有货物 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29807 | 马车白色有货物 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29808 | 马车黑色无货物 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29808 | 马车黑色无货物 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29809 | 马车黑色有货物 | idle | 循环 | 1.60 | model/player/C_L10/malache/L5_mache@idle.fbx |
| 29809 | 马车黑色有货物 | run | 循环 | 0.67 | model/player/C_L10/malache/L5_mache@run.fbx |
| 29821 | 曼波塔 | run02 | 循环 | 0.47 | model/player/C_L14/manbota/manbota@run02.FBX |
| 29821 | 曼波塔 | fakuang | 循环 | 1.80 | model/player/C_L14/manbota/manbota@fakuang.FBX |
| 29821 | 曼波塔 | run | 循环 | 0.53 | model/player/C_L14/manbota/manbota@run.FBX |
| 29834 | 休眠舱 | dakai_loop | 一次 | 0.03 | model/player/C_L14/xiumiancang/xiumiancang@skin.fbx |
| 29834 | 休眠舱 | dakai | 一次 | 1.67 | model/player/C_L14/xiumiancang/xiumiancang@skin.fbx |
| 29834 | 休眠舱 | idle | 一次 | 0.03 | model/player/C_L14/xiumiancang/xiumiancang@skin.fbx |
| 30108 | 评级机器关卡 | penqi | 一次 | 2.00 | model/player/C_L14/yaolukou/sm_l15_fenleijiqi@anim.fbx |
| 30108 | 评级机器关卡 | idle | 一次 | 0.03 | model/player/C_L14/yaolukou/sm_l15_fenleijiqi@anim.fbx |
| 30111 | 胶囊存储器 | dakai | 一次 | 0.67 | model/player/C_L14/jiaonangchucunqi/jiaonangchucunqi@skin.fbx |
| 30111 | 胶囊存储器 | idle | 一次 | 0.03 | model/player/C_L14/jiaonangchucunqi/jiaonangchucunqi@skin.fbx |
| 30111 | 胶囊存储器 | dakai_loop | 一次 | 0.03 | model/player/C_L14/jiaonangchucunqi/jiaonangchucunqi@skin.fbx |
| 30189 | 小核桃emp | idle | 循环 | 1.73 | model/player/C_L14/xiaohetao_emp/xiaohetao_emp@idle.fbx |
| 30435 | 食物箱150 | dakai_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@dakai_idle.fbx |
| 30435 | 食物箱150 | bihe_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@bihe_idle.fbx |
| 30436 | 物资箱150堆叠 | dakai_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@dakai_idle.fbx |
| 30436 | 物资箱150堆叠 | bihe_idle | 循环 | 1.00 | model/player/C_L13/wuzixiang/wuzixiang@bihe_idle.fbx |
| 30437 | 遗迹口大门 | dakai | 一次 | 1.33 | model/player/C_L14/yijikoudamen/sm_l15_yjkdm@skin.fbx |
| 30437 | 遗迹口大门 | guanbi | 一次 | 0.03 | model/player/C_L14/yijikoudamen/sm_l15_yjkdm@skin.fbx |
| 30437 | 遗迹口大门 | dakai_loop | 一次 | 0.03 | model/player/C_L14/yijikoudamen/sm_l15_yjkdm@skin.fbx |
| 30670 | 曼波塔趴地上 | run02 | 循环 | 0.47 | model/player/C_L14/manbota/manbota@run02.FBX |
| 30670 | 曼波塔趴地上 | fakuang | 循环 | 1.80 | model/player/C_L14/manbota/manbota@fakuang.FBX |
| 30670 | 曼波塔趴地上 | run | 循环 | 0.53 | model/player/C_L14/manbota/manbota@run.FBX |

## 速查：按能力分组

### 能播放动画（Animator + 控制器有效）（187 个）

| AssetId | 名称 | prefab |
|---------|------|--------|
| 12582 | 宝箱 | baoxiang.prefab |
| 12588 | 普通机械螃蟹 | pangxie.prefab |
| 14680 | 猫雷达 | maoleida.prefab |
| 14720 | 核桃飞机_3D | hetaofeiji_3D.prefab |
| 14721 | 黄牛_3D | huangniu_3D.prefab |
| 14722 | 队长_3D | nanhai_3D.prefab |
| 14723 | 展喵_3D | zhanmiao_3D.prefab |
| 14724 | 小核桃_3D | xiaohetao02_3D.prefab |
| 14725 | 核桃机甲_3D | hetaojijia_3D.prefab |
| 14727 | 茶杯盖子 | chabeigaizi.prefab |
| 15188 | 智慧核心 | zhihuihexin.prefab |
| 16090 | l4门 | l4_gsgc_men.prefab |
| 16356 | 水池盖子 | shuichigaizidu01.prefab |
| 16406 | 红温保安 | gongchanganbao_hongwen.prefab |
| 16407 | 红温食人花 | shirenhua_hongwen.prefab |
| 16408 | 红温扫地鲲 | saodikun_hongwen.prefab |
| 16409 | 红温机械狗仔 | jixiegouzhaiV01_hongwen.prefab |
| 16410 | 红温螃蟹 | pangxie_hongwen.prefab |
| 16411 | 朱雀 | zhuque.prefab |
| 16413 | 白虎 | baihu.prefab |
| 16599 | 闸门开关 | zhamenkaiguan.prefab |
| 16980 | 卡皮巴拉大炮发射炮弹 | kapibaladapao.prefab |
| 16981 | 时日环 | shirihuan.prefab |
| 16987 | 游动浮光鲤 | fuguangli.prefab |
| 17009 | 打开待机武器箱 | sm_l5_xiangzi_01.prefab |
| 17016 | 蒸汽无人机 | zhengqiwurenji.prefab |
| 17274 | 发光时空之眼 | shikongzhiyan.prefab |
| 17965 | 嘟嘟车 | duduche.prefab |
| 17981 | 监狱门 | jianyumen.prefab |
| 17990 | 检测狗 | jiancegou.prefab |
| 18014 | 天穹仪 | tianqiongyi_01.prefab |
| 18016 | 新版天穹仪 | tianqiongyi_03.prefab |
| 18020 | 投射土豆炮弹的蘑菇土豆天使炮 | mogutudoutianshipao.prefab |
| 18022 | 发射脉冲弹菠萝西瓜脉冲弹 | boluoxiguamaichongdan.prefab |
| 18327 | 鲁班锁 | lubansuo.prefab |
| 18530 | 天穹仪破碎版 | tianqiongyi_posui.prefab |
| 18531 | 嘟嘟车+卡皮巴拉司机 | duduche+siji.prefab |
| 18532 | 嘟嘟车+乘客 | duduche+chengke.prefab |
| 18646 | 食人花 | shirenhua.prefab |
| 18647 | 蒸汽破空 | zhengqipokong_jl.prefab |
| 18652 | 坦克 | tanke.prefab |
| 19851 | 全向车 | yingjian_quanxiangche.prefab |
| 20709 | 全向车_外卖 | yingjian_quanxiangche_hnwm.prefab |
| 20850 | 魔法马车 | mofamache.prefab |
| 20870 | 保安树01 | baoanshu01.prefab |
| 20871 | 保安树02 | baoanshu02.prefab |
| 20872 | 保安树03 | baoanshu03.prefab |
| 20873 | 保安树04 | baoanshu04.prefab |
| 21061 | 无人机 | wurenji.prefab |
| 21064 | 箭头 | jiantou.prefab |
| 21281 | 巨大荷花 | sm_l7_judahehua.prefab |
| 21390 | 神笔-笔杆（半成品）漂浮发光 | sm_l9_dj_shengbi_02.prefab |
| 21397 | 神器合集 | shenqiheji.prefab |
| 21402 | 黑马人脑机接口 | heimarenpaobuji.prefab |
| 21403 | 红马人脑机接口 | hongmarenpaobuji.prefab |
| 21404 | 棕马人脑机接口 | zongheimarenpaobuji.prefab |
| 21406 | 智能小车+厨艺箱 | zhinengxiaoche.prefab |
| 21407 | 智能小车+魔法坩埚 | zhinengxiaoche_mofaganguo.prefab |
| 21574 | 龙宝宝3D精灵 | longbaobao_jingling.prefab |
| 21753 | 智能小车魔药坩埚绿 | zhinengxiaoche_mofaganguo_lv.prefab |
| 21998 | 围栏爬藤_精灵版 | weilanpateng_jl.prefab |
| 22232 | 打招呼的信鸽 | L9_xinge@skin_dazhaohu.prefab |
| 22233 | 待机的信鸽 | L9_xinge@skin_daiji.prefab |
| 22239 | 祈雨大炮_车轮 | qiyudapao_chelun.prefab |
| 22240 | 飞行的信鸽 | L9_xinge@skin_feixing.prefab |
| 22246 | 椅子 | yizi.prefab |
| 22247 | 椅子01 | yizi01.prefab |
| 22248 | 椅子02 | yizi02.prefab |
| 22369 | 会飞的书 | huifeideshu.prefab |
| 22577 | 神笔-笔杆（半成品）漂浮 | qiankunshenbi_02.prefab |
| 22590 | 漂浮 浮动的状态闪现花 | sm_L9_shanxianhua@skin.prefab |
| 22591 | 营地升级-增加武器库 | sm_l9_yingdi_duanzao_01.prefab |
| 22601 | 待机2攻城车 | gongchenghuoche.prefab |
| 22602 | 神笔造墨锦囊 | shenbizaomojinnang.prefab |
| 22614 | 攻城车毁损 | gongchenghuochesunhuaiban.prefab |
| 22623 | 行使1攻城车 | sm_L9_gongchenghuoche_rw.prefab |
| 22624 | 攻击攻城车 | sm_L9_gongchenghuoche_gj.prefab |
| 22625 | 行驶2攻城车 | sm_L9_gongchenghuoche_run.prefab |
| 22626 | 待机1攻城车 | sm_L9_gongchenghuoche_dw.prefab |
| 22765 | 监牢大门打开过程 | sm_l9_jianlaodamen_a.prefab |
| 22772 | 监牢大门关闭 | sm_l9_jianlaodamen_b.prefab |
| 23414 | 全向车_生命罗卜 | quanxiangche_shengmingluobu.prefab |
| 23749 | 小精灵_3D精灵版 | xiaojingling_3Djingling.prefab |
| 23751 | 鹦鹉草叉_3D精灵版 | yingwucaocha_3Djingling.prefab |
| 23753 | 小熊猫马桶撅_3D精灵版 | xiaoxiongmaomatongjue_3Djingling.prefab |
| 23754 | 冷不丁_3D精灵版 | lengbuding_3Djingling.prefab |
| 23794 | 卡皮巴拉士兵06_3D精灵版 | kapibalashibing06_3Djingling.prefab |
| 23795 | 粉红河马_3D精灵版 | fenhonghema_chengnian_3Djingling.prefab |
| 23797 | 土拨鼠长老红_3D精灵版 | tuboshuzhanglao_red_3Djingling.prefab |
| 23798 | 土拨鼠长老绿_3D精灵版 | tuboshuzhanglao_green_3Djingling.prefab |
| 23799 | 土拨鼠长老蓝_3D精灵版 | tuboshuzhanglao_blue_3Djingling.prefab |
| 23909 | 火烈鸟棒子（欧阳版） | huolieniao_bangzi.prefab |
| 23930 | 玫瑰花 | meiguihua.prefab |
| 23931 | 倒计时玫瑰花 | meiguihua_daojishi.prefab |
| 23944 | 棒打柠檬药水满杯 | sm_nmys_man.prefab |
| 23967 | 大礼帽3D精灵版 | dalimao_3Djingling.prefab |
| 23970 | 疯帽匠+大礼帽 | fengmaojiang_dalimao.prefab |
| 24137 | 疯帽匠3D精灵版 | fengmaojiang_3Djingling.prefab |
| 24155 | 老毛虫 | laomaochong.prefab |
| 24173 | 快问快答卷 | kwkdj.prefab |
| 24174 | 朋友肖像卷 | xxj.prefab |
| 24175 | 茧 | jian.prefab |
| 24176 | 茧房 | jianfang.prefab |
| 24184 | 茶壶女茶杯男 | chahunv+chabeinan.prefab |
| 24198 | 黄色咖啡杯带动画 | chabei01.prefab |
| 24199 | 绿色咖啡杯带动画 | chabei02.prefab |
| 24344 | 蓝色茶壶动画版 | lansechahu.prefab |
| 24345 | 棕色茶壶动画版 | zongsechahu.prefab |
| 24346 | 粉丝茶壶动画版 | fensechahu.prefab |
| 24347 | 紫色茶壶动画版 | zisechahu.prefab |
| 24400 | 百灵扫帚女童 | bailingsaozhounvtong.prefab |
| 25080 | 贝壳珍珠 | beikezhenzhu.prefab |
| 25479 | 寻龙分金尺 | fenjinchi.prefab |
| 25480 | 千面神灯 | qianmianshendeng.prefab |
| 25609 | 社牛水晶球_带动画 | sheniushuijingqiu.prefab |
| 25843 | 精灵果盘 | jinglingguopan.prefab |
| 25850 | 水晶圈 | shuijinquan.prefab |
| 25852 | 智能小车混沌星核 | zhinengxiaoche_chaoshenbochuanganqi.prefab |
| 25853 | 招财猫 | zhaocaimao.prefab |
| 26567 | 希斯发3D精灵 | xisifa_3Djingling.prefab |
| 26692 | 特斯拉时空跑车崭新版 | tesilapaoche_zhanxinban.prefab |
| 26693 | 特斯拉时空跑车灰尘版 | tesilapaoche_huichenban.prefab |
| 26918 | 希斯发未黑化3D精灵版 | xisifa_weiheihua_3djingling.prefab |
| 27068 | 机械臂全向车 | jixiebiquanxiangche.prefab |
| 27083 | 特斯拉时空跑车发光 | tesilapaoche_faguang.prefab |
| 27239 | 机械臂全向车 | jixiebiquanxiangche_jixiebi.prefab |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | jixiebiquanxiangche_jixiebi_jianzhubaoguo.prefab |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | jixiebiquanxiangche_jixiebi_mozhibaoguo.prefab |
| 27392 | 曼德拉草3D精灵 | mandelacao_3Djingling.prefab |
| 27393 | 矮人3D精灵 | airen_3Djingling.prefab |
| 27416 | 王者之剑带动作 | wangzhezhijian_daidongzuo.prefab |
| 27489 | 王者之剑火焰特效版带动作 | wangzhezhijian_daidongzuo_huoyantexiao.prefab |
| 27534 | 机械臂全向车装满草 | jixiebiquanxiangche_jixiebi_zhuangmancao.prefab |
| 27535 | 机械臂全向车夹草 | jixiebiquanxiangche_jixiebi_jiacao.prefab |
| 27536 | 机械臂全向车夹坩埚 | jixiebiquanxiangche_jixiebi_zhuangmancao_jiaganguo.prefab |
| 27549 | 机械臂全向车装货框版 | jixiebiquanxiangche_jixiebi_zhuanghuokuang.prefab |
| 27551 | 队长魔法袍03_3D精灵 | duizhangmofapaoshengji03_3D.prefab |
| 27552 | 雪球0_5_3D精灵 | xueqiuL0_5_3D.prefab |
| 27553 | 桃子魔法袍_3D精灵 | taozimofapao_3D.prefab |
| 27554 | 乌拉乎魔法袍_3D精灵 | wulahumofapao_3D.prefab |
| 27555 | 禾木魔法袍_3D精灵 | hemumofapao_3D.prefab |
| 27956 | 智能小车混沌星核无超声传感 | zhinengxiaoche_hundunxinghe_wuchuanganqi.prefab |
| 28055 | 雷达 | sm_l13_leida.prefab |
| 28070 | 无人机 | L13_wurenji.prefab |
| 28106 | 物资箱带动画 | wuzixiang_daidonghua.prefab |
| 28107 | 风车 | sm_l6_dj_fengche01.prefab |
| 28108 | 魔药园风车建筑 | sm_l7_dj_myy_fengche.prefab |
| 28264 | 物资箱带动画02 | wuzixiang_daidonghua02.prefab |
| 28273 | 雷达带动画 | leida_anim.prefab |
| 28364 | 物资库大门 | wuzikudamen.prefab |
| 28679 | 矿洞大门 | sm_l15_kg_men.prefab |
| 28999 | 全向车机械臂货框颜色传感器 | jixiebiquanxiangche_jixiebi_huowukuai.prefab |
| 29009 | 降维陨石碎片 | jiangweiyunshi_suipian.prefab |
| 29111 | 脑电波机 | hemunaodianboji.prefab |
| 29157 | 窑炉口 | sm_l15_fenleijiqi.prefab |
| 29243 | 分割机器 | fengejiqi.prefab |
| 29265 | 盲盒 | manghe.prefab |
| 29275 | 物资箱打开 | wuzixiang_daidonghua_dakai.prefab |
| 29276 | 物资箱打开02 | wuzixiang_daidonghua02_dakai.prefab |
| 29290 | 食物箱 | wuzixiang_shiwu.prefab |
| 29291 | 食物箱打开状态 | wuzixiang_shiwu_dakai.prefab |
| 29297 | 漫波神庙大门 | manboshenmiao_damen.prefab |
| 29298 | 漫波大神庙密码门 | manbodashenmiao_mimamen.prefab |
| 29299 | 切割机器 | qiegejiqi.prefab |
| 29334 | 钟表 | zhongbiao.prefab |
| 29633 | 马车 | sm_l14_mache01.prefab |
| 29637 | 榴莲 | liulian.prefab |
| 29638 | 榴莲坏了 | liulian_huai.prefab |
| 29661 | 曼德拉草_捕狼草 | mandelacao_3Djingling_bulangcao.prefab |
| 29663 | 商人货车白 | sm_l14_mache03.prefab |
| 29664 | 商人货车黑 | sm_l14_mache02.prefab |
| 29675 | 护卫机甲 | sm_gk_mofarenou1.prefab |
| 29804 | 马车黄色无货物 | mache_huang_wuhuo.prefab |
| 29805 | 马车黄色有货物 | mache_huang_youhuowu.prefab |
| 29806 | 马车白色无货物 | mache_bai_wuhuo.prefab |
| 29807 | 马车白色有货物 | mache_bai_youhuowu.prefab |
| 29808 | 马车黑色无货物 | mache_hei_wuhuo.prefab |
| 29809 | 马车黑色有货物 | mache_hei_youhuowu.prefab |
| 29821 | 曼波塔 | manbota.prefab |
| 29834 | 休眠舱 | xiumiancang.prefab |
| 30108 | 评级机器关卡 | sm_gk_pjjq.prefab |
| 30111 | 胶囊存储器 | jiaonangchucunqi.prefab |
| 30189 | 小核桃emp | xiaohetao_emp.prefab |
| 30435 | 食物箱150 | wuzixiang_150.prefab |
| 30436 | 物资箱150堆叠 | wuzixiang_150duidie.prefab |
| 30437 | 遗迹口大门 | yijikoudamen.prefab |
| 30670 | 曼波塔趴地上 | manbota_padi.prefab |

### 带骨骼/蒙皮（SkinnedMeshRenderer）（19 个）

| AssetId | 名称 | prefab |
|---------|------|--------|
| 12582 | 宝箱 | baoxiang.prefab |
| 15188 | 智慧核心 | zhihuihexin.prefab |
| 18014 | 天穹仪 | tianqiongyi_01.prefab |
| 18016 | 新版天穹仪 | tianqiongyi_03.prefab |
| 18530 | 天穹仪破碎版 | tianqiongyi_posui.prefab |
| 22232 | 打招呼的信鸽 | L9_xinge@skin_dazhaohu.prefab |
| 22233 | 待机的信鸽 | L9_xinge@skin_daiji.prefab |
| 22240 | 飞行的信鸽 | L9_xinge@skin_feixing.prefab |
| 22590 | 漂浮 浮动的状态闪现花 | sm_L9_shanxianhua@skin.prefab |
| 22591 | 营地升级-增加武器库 | sm_l9_yingdi_duanzao_01.prefab |
| 22772 | 监牢大门关闭 | sm_l9_jianlaodamen_b.prefab |
| 27240 | 机械臂全向车+机械臂+建筑包裹 | jixiebiquanxiangche_jixiebi_jianzhubaoguo.prefab |
| 27241 | 机械臂全向车+机械臂+魔植包裹 | jixiebiquanxiangche_jixiebi_mozhibaoguo.prefab |
| 27956 | 智能小车混沌星核无超声传感 | zhinengxiaoche_hundunxinghe_wuchuanganqi.prefab |
| 28108 | 魔药园风车建筑 | sm_l7_dj_myy_fengche.prefab |
| 28999 | 全向车机械臂货框颜色传感器 | jixiebiquanxiangche_jixiebi_huowukuai.prefab |
| 29140 | 窑炉    窑炉口1 | sm_l15_yaoluko.prefab |
| 29297 | 漫波神庙大门 | manboshenmiao_damen.prefab |
| 29298 | 漫波大神庙密码门 | manbodashenmiao_mimamen.prefab |

### 自带粒子特效（4 个）

| AssetId | 名称 | prefab |
|---------|------|--------|
| 25522 | 楼梯指示牌 | sm_l9_dj_lupai.prefab |
| 29140 | 窑炉    窑炉口1 | sm_l15_yaoluko.prefab |
| 29297 | 漫波神庙大门 | manboshenmiao_damen.prefab |
| 29298 | 漫波大神庙密码门 | manbodashenmiao_mimamen.prefab |

### 可穿过（Trigger）（248 个）

| AssetId | 名称 | prefab |
|---------|------|--------|
| 13363 | 石台 | sm_shitai.prefab |
| 14640 | 蜜雪冰牛奶茶粉 | sm_mixuebingniu_fen.prefab |
| 14641 | 蜜雪冰牛奶茶黄 | sm_mixuebingniu_huang.prefab |
| 14644 | 棍棒 | sm_langyabang.prefab |
| 14645 | 草叉 | sm_yucha.prefab |
| 14646 | 马桶撅 | sm_matongsai.prefab |
| 14649 | 昆仑灵芝 | sm_lingzhi_01.prefab |
| 14651 | 天山雪莲 | sm_lianhua.prefab |
| 14652 | 特制炼丹鼎 | sm_ding.prefab |
| 14653 | 九转还魂丹 | sm_qiu.prefab |
| 14655 | 红豆竹筐 | sm_zhukuang_hongdou.prefab |
| 14668 | 海州衙门桌子 | sm_haizhouyamen_zhuozi.prefab |
| 14671 | 被污染的昆仑灵芝 | sm_wuranlingzhi.prefab |
| 14732 | 鉴宝机 | sm_l3_jianbaoji.prefab |
| 14758 | 破船 | sm_l3_pochuan.prefab |
| 14761 | 密室大门 | sm_l3_mimasuo_damen.prefab |
| 15074 | 密码锁1 | sm_l3_mimasuo_06.prefab |
| 15075 | 密码锁2 | sm_l3_mimasuo_05.prefab |
| 15076 | 密码锁3 | sm_l3_mimasuo_07.prefab |
| 15077 | 密码锁4 | sm_l3_mimasuo_08.prefab |
| 15078 | 密码锁（源代码化） | sm_mimasuo.prefab |
| 15079 | 清道夫 | sm_l3_qingdaofu.prefab |
| 15080 | 水瓶 | sm_l3_shuiping.prefab |
| 15081 | 神秘宝石 （机关球） | sm_l3_shenmibaoshi.prefab |
| 15082 | 碎布 | sm_l3_suibu.prefab |
| 15189 | 秋生账本 | sm_l3_qiushegnzhangben.prefab |
| 15285 | 自动投喂机 | sm_l3_jiingwangweishiji_po.prefab |
| 15286 | 密码手册 | sm_l3_mimashouce.prefab |
| 15863 | 自动投喂机说明书 | sm_l3_shuomingshu.prefab |
| 16086 | 蒙汗药01 | sm_kejianbuji_menghanyao_01.prefab |
| 16087 | 蒙汗药02 | sm_kejianbuji_menghanyao_02.prefab |
| 16382 | 金字塔 | sm_l4_jinzita.prefab |
| 16383 | 虎身人面像 | sm_l4_baihu.prefab |
| 16384 | pad | sm_l4_pad.prefab |
| 16385 | 蒸汽宝典 | sm_l4_zhengqibaodian.prefab |
| 16386 | 进化芯片中 | sm_l4_jinhuaxinpian_02.prefab |
| 16387 | 进化芯片小 | sm_l4_jinhuaxinpian.prefab |
| 16388 | 兴奋薄荷的能量果实车 | sm_l4_daoju_qiche_04.prefab |
| 16389 | 白菜的能量果实车 | sm_l4_daoju_qiche_05.prefab |
| 16390 | 生命萝卜的能量果实车 | sm_l4_daoju_qiche_01.prefab |
| 16391 | 防御椰子能量果实车 | sm_l4_daoju_qiche_03.prefab |
| 16392 | 敏捷香蕉能量果实车 | sm_l4_daoju_qiche_02.prefab |
| 16394 | 能源矿车 | sm_l4_daoju_chexiang.prefab |
| 16395 | 躺平西瓜 | sm_l4_bindongxigua.prefab |
| 16396 | 碎石1 | sm_l4_suishi_01.prefab |
| 16397 | 碎石2 | sm_l4_suishi_02.prefab |
| 16398 | 碎石3 | sm_l4_suishi_03.prefab |
| 16399 | 木牌子 | sm_l4_mupai.prefab |
| 16400 | 梼杌（曾用名貔貅）大脚 | sm_l4_dajiao.prefab |
| 16401 | 梼杌（曾用名貔貅）大头 | sm_l4_datou.prefab |
| 16402 | 冰块碎石1 | sm_l4_suibing_01.prefab |
| 16403 | 冰块碎石2 | sm_l4_suibing_02.prefab |
| 16404 | 冰块碎石3 | sm_l4_suibing_03.prefab |
| 16405 | 冰块碎石4 | sm_l4_suibing_04.prefab |
| 16410 | 红温螃蟹 | pangxie_hongwen.prefab |
| 16412 | 青龙 | sm_l4_qinglong.prefab |
| 16413 | 白虎 | baihu.prefab |
| 16416 | 条幅 | sm_l4_hengfu_01.prefab |
| 16417 | 纸张1 | sm_l4_feizhi_01.prefab |
| 16418 | 纸张2 | sm_l4_feizhi_02.prefab |
| 16419 | 毛笔 | sm_l4_maobi_01.prefab |
| 16455 | 地图碎片3 | sm_ditusuipian_03.prefab |
| 16456 | 地图碎片2 | sm_ditusuipian_02.prefab |
| 16457 | 地图碎片1 | sm_ditusuipian_01.prefab |
| 16458 | 桃源山全图 | sm_ditusuipian.prefab |
| 16956 | 星座壁画 | sm_l4_xingzuobihua.prefab |
| 17001 | 大日晷 | sm_l5_darigui.prefab |
| 17002 | 小日晷 | sm_l5_xiaorigui.prefab |
| 17003 | 古代瓦罐 | sm_l5_gudaiwaguan.prefab |
| 17004 | 火晶 | sm_l5_huojing.prefab |
| 17005 | 将军令牌 | sm_l5_jiangjunlingpai.prefab |
| 17008 | 木咋特鸟蛋2 | sm_l5_daoju_dan_02.prefab |
| 17014 | 进化芯片大 | sm_l4_jinhuaxinpian_03.prefab |
| 17263 | 星座壁画 虎 | sm_l4_xingzuobihua_hu.prefab |
| 17264 | 星座壁画 鹊 | sm_l4_xingzuobihua_que.prefab |
| 17292 | 被打断消失飞箭 | sm_l5_feijian_daduan.prefab |
| 17293 | 被打断消失箭雨 | sm_l5_jianyu_daduan.prefab |
| 17391 | 飞箭 | sm_l5_feijian.prefab |
| 17392 | 箭雨 | sm_l5_jianyu.prefab |
| 17393 | 一堆黄金香蕉 | sm_l5_yiduihuangjinxiangjiao.prefab |
| 17394 | 一根黄金香蕉 | sm_l5_yigenhuangjinxiangjiao.prefab |
| 17395 | 锦囊 | sm_L5_jinnang.prefab |
| 17398 | 牢笼 | sm_l2_laolong.prefab |
| 17564 | 燃烧的火晶 | sm_l5_huojing02.prefab |
| 17567 | 喵朝军营帐篷完整 | sm_l5_hdzk_jianzhu_02.prefab |
| 17568 | 待机时空之眼 | sm_l5_shikongzhiyan.prefab |
| 17569 | 损坏侧翻卡皮巴拉大炮 | sm_l5_kapibaladapao_2.prefab |
| 17571 | 卡皮巴拉军营帐篷 | sm_l5_kapibala.prefab |
| 17573 | 发光大日晷 | sm_l5_darigui02.prefab |
| 17574 | 发光小日晷 | sm_l5_xiaorigui02.prefab |
| 17576 | 胡萝卜 | sm_l5_hulubo.prefab |
| 17577 | 待机大蒸汽战舰 | sm_l5_kpbl_zhanchuan_01.prefab |
| 17578 | 小蒸汽战舰 | sm_l5_weicheng_xiaochuan.prefab |
| 17579 | 待机浮光鲤 | sm_l5_fuguangli.prefab |
| 17955 | 关闭待机武器箱 | sm_l5_xiangzi_02.prefab |
| 17956 | 持续出现电流武器箱 | sm_l5_xiangzi_03.prefab |
| 17991 | 佛系解毒丹 | sm_l6_jieduwan.prefab |
| 17992 | 金蛋1 | sm_l6_dan_01.prefab |
| 17993 | 金蛋2 | sm_l6_dan_02.prefab |
| 17994 | 金蛋3 | sm_l6_dan_03.prefab |
| 17995 | 金蛋4 | sm_l6_dan_04.prefab |
| 17996 | 金蛋5 | sm_l6_dan_05.prefab |
| 17997 | 金蛋6 | sm_l6_dan_06.prefab |
| 17998 | 金蛋7 | sm_l6_dan_07.prefab |
| 17999 | 金蛋8 | sm_l6_dan_08.prefab |
| 18000 | 金蛋9 | sm_l6_dan_09.prefab |
| 18001 | 空白金蛋 | sm_l6_dan_10.prefab |
| 18002 | 砸开金蛋1 | sm_l6_dan_posun_01.prefab |
| 18003 | 砸开金蛋2 | sm_l6_dan_posun_02.prefab |
| 18004 | 砸开金蛋3 | sm_l6_dan_posun_03.prefab |
| 18005 | 砸开金蛋4 | sm_l6_dan_posun_04.prefab |
| 18006 | 砸开金蛋5 | sm_l6_dan_posun_05.prefab |
| 18007 | 砸开金蛋6 | sm_l6_dan_posun_06.prefab |
| 18009 | 砸开金蛋空白 | sm_l6_dan_posun_10.prefab |
| 18010 | 砸金蛋锤 | sm_l6_zadanchuizi.prefab |
| 18011 | 金鸡兽宝箱 | sm_l6_baoxiang.prefab |
| 18012 | 豪宅券 | sm_l6_juan_02.prefab |
| 18013 | 免费御膳券 | sm_l6_juan_01.prefab |
| 18017 | 盖世英雄金锅锅 | sm_l6_tianqiongyi_04.prefab |
| 18019 | 蘑菇土豆天使炮 | sm_l6_mogutudoutianshipao.prefab |
| 18020 | 投射土豆炮弹的蘑菇土豆天使炮 | mogutudoutianshipao.prefab |
| 18022 | 发射脉冲弹菠萝西瓜脉冲弹 | boluoxiguamaichongdan.prefab |
| 18358 | 土 | sm_l6_zhiwushitou_01.prefab |
| 18359 | 凹凸曼西瓜 | sm_l6_xigua.prefab |
| 18360 | 天使蘑菇 | sm_l6_mogu.prefab |
| 18361 | 超级菠萝 | sm_l6_boluo.prefab |
| 18362 | 傲娇白菜 | sm_l6_dabaicai_01.prefab |
| 18363 | 拽酷仙人掌 | sm_l6_xianrenzhang_01.prefab |
| 18525 | 检测结果出现代码 | sm_l6_jiancejieguo.prefab |
| 18658 | 大乌云 | sm_l6_wuyun_02.prefab |
| 19283 | 马车 | sm_dh_mache.prefab |
| 19352 | 定水神针 | sm_kejianbuji_jingubang.prefab |
| 19354 | 黑色大山 | sm_cg_heisedashan.prefab |
| 20167 | 黑色直线 | sm_zhixianheixian.prefab |
| 20168 | 转弯黑线 | sm_zhuanwanheixian.prefab |
| 20169 | 重点区域 | sm_zhongdianquyu.prefab |
| 20170 | 积雪 | sm_l4_xuekuai_01.prefab |
| 20172 | 大冰块 | sm_yj_dabingkuai.prefab |
| 20758 | 传奇法袍 | sm_L7_chuanqifapao.prefab |
| 20824 | 魔法马车 | sm_l7_mofamache.prefab |
| 20829 | 飞剑 | sm_L7_feijian.prefab |
| 20831 | 传奇魔杖 | sm_L7_chuanqimozhang.prefab |
| 20837 | 普通法袍 | sm_l7_putongfapao.prefab |
| 20841 | 时间之匙（完整） | sm_l7_yaoshi_01.prefab |
| 20842 | 时间之匙碎片01 | sm_l7_yaoshisuipian_01.prefab |
| 20843 | 时间之匙碎片02 | sm_l7_yaoshisuipian_02.prefab |
| 20844 | 时间之匙碎片03 | sm_l7_yaoshisuipian_03.prefab |
| 20845 | 时间之匙碎片04 | sm_l7_yaoshisuipian_04.prefab |
| 20846 | 时间之匙碎片05 | sm_l7_yaoshisuipian_05.prefab |
| 20847 | 时间之匙碎片06 | sm_l7_yaoshisuipian_06.prefab |
| 20851 | 现代汽车01 | sm_l7_Car_01.prefab |
| 20925 | 毒刺 | sm_l7_duci.prefab |
| 21035 | 魔法三色灯亮红灯 | sm_l7_daoju_sansedeng_hong.prefab |
| 21038 | 普通魔镜 | sm_l7_daoju_mojing_02.prefab |
| 21281 | 巨大荷花 | sm_l7_judahehua.prefab |
| 21286 | 运输路线-运送目的地 | sm_l8_yunsumudidi.prefab |
| 21288 | 运输路线-绿色方块区域 | sm_l8_yunsuluxianfangkuai.prefab |
| 21289 | 运输路线-棕色方块区域 | sm_l8_yunsuluxianfangkuai02.prefab |
| 21301 | 自动行驶路线图 | sm_l8_luxiantu.prefab |
| 21302 | 取货送货路线图 | sm_l8_luxiantu02.prefab |
| 21305 | 黑将 | sm_L8_jiang.prefab |
| 21306 | 黑士 | sm_L8_shi.prefab |
| 21308 | 黑车 | sm_L8_che.prefab |
| 21309 | 红炮 | sm_L8_pao02.prefab |
| 21310 | 红车 | sm_L8_che02.prefab |
| 21312 | 红帅 | sm_L8_jiang02.prefab |
| 21313 | 马撕客旗子 | sm_l8_dj_mskqz.prefab |
| 21314 | 激励马人横幅 | sm_l8_dj_hengfu.prefab |
| 21315 | 红仕 | sm_L8_shi02.prefab |
| 21316 | 黑砲 | sm_L8_pao.prefab |
| 21317 | 装魔药的坩埚 | sm_l8_daoju_myqg.prefab |
| 21318 | 花瓣账单 | sm_l8_daoju_huaban.prefab |
| 21320 | 不一定唤龙笛 | sm_l8_longdi.prefab |
| 21388 | 打字机 | sm_l9_dj_daziji.prefab |
| 21389 | 借阅记录 | sm_l9_dj_jyjl.prefab |
| 21392 | 神笔造墨锦囊 | sm_l9_dj_zmjn.prefab |
| 21393 | 隐形兽尾毛 | sm_l9_dj_weimao.prefab |
| 21394 | 纸团 | sm_l9_dj_zhituan.prefab |
| 21548 | 路线 | sm_l8_luxian.prefab |
| 21581 | 魔植白术 | sm_l8_daoju_baishu.prefab |
| 21582 | 魔植茯苓 | sm_l8_daoju_fuling.prefab |
| 21585 | 字母龙鳞a | sm_L8_zimulonglina.prefab |
| 21586 | 字母龙鳞b | sm_L8_zimulonglinb.prefab |
| 21588 | 字母龙鳞k | sm_L8_zimulonglink.prefab |
| 21589 | 字母龙鳞m | sm_L8_zimulonglinm.prefab |
| 21590 | 字母龙鳞o | sm_L8_zimulonglino.prefab |
| 21591 | 字母龙鳞z | sm_L8_zimulonglinz.prefab |
| 21595 | 烤糊土层1 | sm_l8_caidi_01.prefab |
| 21596 | 烤糊土层2 | sm_l8_caidi_02.prefab |
| 22120 | 装相片的箱子 | sm_l8_daoju_baoxiang.prefab |
| 22131 | 桥板数字2 | sm_l9_banqiao_2.prefab |
| 22132 | 桥板数字5 | sm_l9_banqiao_5.prefab |
| 22133 | 桥板数字7 | sm_l9_banqiao_7.prefab |
| 22134 | 桥板数字9 | sm_l9_banqiao_9.prefab |
| 22135 | 桥板英文 i | sm_l9_banqiao_i.prefab |
| 22136 | 桥板英文k | sm_l9_banqiao_k.prefab |
| 22137 | 桥板英文n | sm_l9_banqiao_n.prefab |
| 22240 | 飞行的信鸽 | L9_xinge@skin_feixing.prefab |
| 22441 | 浮空魔法U | sm_l9_dj_mofazhuan_u.prefab |
| 22442 | 浮空魔法砖01 | sm_l9_dj_mofazhuan_01.prefab |
| 22443 | 浮空魔法砖02 | sm_l9_dj_mofazhuan_02.prefab |
| 22444 | 浮空魔法砖03 | sm_l9_dj_mofazhuan_03.prefab |
| 22445 | 浮空魔法砖04 | sm_l9_dj_mofazhuan_04.prefab |
| 22446 | 浮空魔法砖C | sm_l9_dj_mofazhuan_c.prefab |
| 22447 | 浮空魔法砖F | sm_l9_dj_mofazhuan_f.prefab |
| 22448 | 浮空魔法砖o | sm_l9_dj_mofazhuan_o.prefab |
| 22449 | 浮空魔法砖T | sm_l9_dj_mofazhuan_t.prefab |
| 22581 | 冰箭 | sm_l9_bingjian_01.prefab |
| 22582 | 锻造材料堆金子 | sm_l9_dj_cailiaodui_02.prefab |
| 22583 | 锻造材料堆木头 | sm_l9_dj_cailiaodui_01.prefab |
| 22584 | 锻造材料堆石头 | sm_l9_dj_cailiaodui_04.prefab |
| 22585 | 锻造材料堆铁矿 | sm_l9_dj_cailiaodui_03.prefab |
| 22586 | 环湖马拉松奖杯 | sm_l9_jiangbei.prefab |
| 22587 | 金色墨水 | sm_l9_jinsemoshui.prefab |
| 22589 | 玉墨 | sm_l9_dj_yumo.prefab |
| 22595 | 大炮 | sm_L9_qiyudapao_chelun.prefab |
| 22617 | 发光神笔造墨锦囊 | sm_l9_dj_zmjn02.prefab |
| 22749 | 枯萎月光藤-幼苗 | sm_L9_yueguangteng_youmiaokuwei.prefab |
| 22761 | 月光藤-成熟（结果） | sm_L9_yueguangteng_chengshu.prefab |
| 22762 | 月光藤果实 | sm_L9_yueguangteng_guoshi.prefab |
| 22763 | 正常月光藤-幼苗 | sm_L9_yueguangteng_youmiao.prefab |
| 22772 | 监牢大门关闭 | sm_l9_jianlaodamen_b.prefab |
| 24172 | 行李 | sm_l10_xingli.prefab |
| 24685 | 驱狼铃 | sm_l10_qll.prefab |
| 25284 | 咒语残本 | sm_l11_zycb.prefab |
| 25463 | 地球仪 | sm_l11_diqiuyi.prefab |
| 25464 | 天平 | sm_l11_tianping.prefab |
| 27394 | 魔法加特林 | sm_L9_ouyang_wuqi1.prefab |
| 27693 | 毕业典礼横幅 | sm_l12_hengfu.prefab |
| 27816 | 0 | sm_0.prefab |
| 27817 | 1 | sm_1.prefab |
| 27818 | 2 | sm_2.prefab |
| 27819 | 3 | sm_3.prefab |
| 27820 | 4 | sm_4.prefab |
| 27821 | 5 | sm_5.prefab |
| 27822 | 6 | sm_6.prefab |
| 27823 | 7 | sm_7.prefab |
| 27824 | 8 | sm_8.prefab |
| 27825 | 9 | sm_9.prefab |
| 28055 | 雷达 | sm_l13_leida.prefab |
| 28065 | 生物编码药剂粉 | sm_L13shengwubianmayaoji02.prefab |
| 28066 | 生物编码药剂绿 | sm_L13shengwubianmayaoji.prefab |
| 28080 | 组装材料 零件箱 | sm_l13_dzgjx.prefab |
| 28273 | 雷达带动画 | leida_anim.prefab |
| 28749 | 陨石 | sm_l13_yunshi.prefab |
| 29359 | 岩浆发电机 | sm_l14_fadianji.prefab |
| 29934 | 黑土块 | sm_l14_heitukuai.prefab |
| 30459 | 胶囊存储器 | sm_L14_jiaonangchucunqi.prefab |

### 无碰撞体（视觉装饰）（19 个）

| AssetId | 名称 | prefab |
|---------|------|--------|
| 15073 | 密室大门-2 | sm_mimasuodameng_02.prefab |
| 22138 | 搭桥材料堆 | sm_l9_banqiao.prefab |
| 24185 | 堆成山的卷子 | sm_l10_yiduijuanzi.prefab |
| 25276 | 好事坏事全看见魔法屏01 | sm_l10_mfpwenzi_01.prefab |
| 25277 | 好事坏事全看见魔法屏02 | sm_l10_mfpwenzi_02.prefab |
| 25278 | 好事坏事全看见魔法屏03 | sm_l10_mfpwenzi_03.prefab |
| 28084 | 组装材料面板堆01b | sm_l13_mianbandui01b.prefab |
| 28085 | 组装材料面板堆02a | sm_l13_mianbandui01a.prefab |
| 28111 | 太阳能光合板（成组） | sm_l13_taiyangban.prefab |
| 28658 | 材料板1-1 | sm_l13_bingkuai02_1.prefab |
| 28659 | 材料条1 1-1 | sm_l13_bingkuai001_1.prefab |
| 28660 | 材料条2 | sm_l13_bingkuai002_1.prefab |
| 28661 | 材料条3 1-1 | sm_l13_bingkuai003_1.prefab |
| 28662 | 单格冰块1-1 | sm_l13_bingkuai_1.prefab |
| 28663 | 营地地砖1-1 | sm_l13_dizhuan_1.prefab |
| 28664 | 水泥地砖1-1 | sm_l13_dizhuan02_1.prefab |
| 28740 | 小版组装材料版 | sm_l13_mianbandui01a02.prefab |
| 28748 | 关卡 太阳能板 | sm_l13_taiyangnengban.prefab |
| 30473 | 一篮子石墨 | sm_gk_ylzsm.prefab |

