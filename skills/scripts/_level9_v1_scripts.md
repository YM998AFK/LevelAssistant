# e28f86cb-c98d-4bb8-9932-8eb6e33d72f7.ws

## props2 (scene-level vars, initial)
  cid = {"type": "Simple", "value": "0"}
  i = {"type": "Simple", "value": "0"}
  cin_cut = {"type": "SimpleList", "value": []}
  err_msg = {"type": "Simple", "value": "0"}
  #EVENT = {"type": "SimpleList", "value": ["CMD_NewMessage", "初始化", "传递失败", "传递成功", "结束判断", "展示关卡效果", "对话", "换分镜", "打开物资", "显示物资量", "显示结果", "关闭物资箱", "物资准备", "跑到位置"]}


### scene/services/Camera/BlockScript [BlockScript] in <BlockScript> (4 fragments)
--- fragment #0 ---
TransitToCameraPreset('default', 'fade', 'none')
--- fragment #1 ---
WhenReceiveMessage('初始化')
  TransitToCameraPreset('分镜-初始', 'none', 'none')
--- fragment #2 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.2')
  IfElse(    IsEqual(      Variable('cid'), {}, '1'))
    TransitToCameraPreset('分镜-1', 'fade', 'circle')
  else:
    TransitToCameraPreset('分镜-2', 'fade', 'circle')
--- fragment #3 ---
WhenReceiveMessage('对话')
  GlideSecsToPosition3D('0.5', '2019', '2075', '67')

### scene/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('传递成功')
  PlaySound('结算效果-成功')
  PlayAnimationUntil('任务成功')
  WaitSeconds('3')
  EndRun('运行结束', '')
  StopScript('all')
--- fragment #1 ---
WhenReceiveMessage('传递失败')
  PlaySound('结算效果-失败')
  PlayAnimationUntil('任务失败')
  WaitSeconds('3')
  BroadcastMessageAndWait('初始化')
  StopScript('other scripts in sprite')
  EndRun('没过关',     Variable('err_msg'))
  StopScript('all')
--- fragment #2 ---
WhenGameStarts()
  Forever()
    PlaySoundUntil('冒险探索1')

### scene/物资箱带动画 1/BlockScript [BlockScript] in <BlockScript> (5 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '1930', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('i'), {}, '0'))
    WaitSeconds('0.4')
    PlayAnimation('dakai_idle')
--- fragment #2 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('i'), {}, '1'))
    WaitSeconds('0.4')
    PlayAnimation('bihe_idle')
--- fragment #3 ---
WhenReceiveMessage('打开物资')
  WaitSeconds('0.4')
  PlaySound('箱子打开')
--- fragment #4 ---
WhenReceiveMessage('关闭物资箱')
  WaitSeconds('0.4')
  PlaySound('关门音效')

### scene/物资箱带动画 2/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '1960', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('i'), {}, '1'))
    WaitSeconds('0.4')
    PlayAnimation('dakai_idle')
--- fragment #2 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('i'), {}, '2'))
    WaitSeconds('0.4')
    PlayAnimation('bihe_idle')

### scene/物资箱带动画 3/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '1990', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('i'), {}, '3'))
    WaitSeconds('0.4')
    PlayAnimation('bihe_idle')
--- fragment #2 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('i'), {}, '2'))
    WaitSeconds('0.4')
    PlayAnimation('dakai_idle')

### scene/物资箱带动画 4/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2020', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('i'), {}, '4'))
    WaitSeconds('0.4')
    PlayAnimation('bihe_idle')
--- fragment #2 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('i'), {}, '3'))
    WaitSeconds('0.4')
    PlayAnimation('dakai_idle')

### scene/物资箱带动画 5/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2050', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('i'), {}, '5'))
    WaitSeconds('0.4')
    PlayAnimation('bihe_idle')
--- fragment #2 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('i'), {}, '4'))
    WaitSeconds('0.4')
    PlayAnimation('dakai_idle')

### scene/物资箱带动画 6/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2080', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('关闭物资箱')
--- fragment #2 ---
If(  IsEqual(    Variable('i'), {}, '6'))
  PlayAnimation('bihe_idle')

### scene/物资箱带动画 7/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2110', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('关闭物资箱')
--- fragment #2 ---
If(  IsEqual(    Variable('i'), {}, '7'))
  PlayAnimation('bihe_idle')

### scene/物资箱带动画 8/BlockScript [BlockScript] in <BlockScript> (1 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2140', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})

### scene/物资箱带动画 9/BlockScript [BlockScript] in <BlockScript> (1 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2170', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})

### scene/物资箱带动画 10/BlockScript [BlockScript] in <BlockScript> (1 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '2200', '-6')
  PointInDirection({}, '90')
  SetSize({}, '70')
  Show({})

### scene/桃子星际服/BlockScript [BlockScript] in <BlockScript> (14 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
--- fragment #1 ---
WhenReceiveMessage('对话')
--- fragment #2 ---
WhenReceiveMessage('换分镜')
--- fragment #3 ---
WhenReceiveMessage('打开物资')
--- fragment #4 ---
WhenReceiveMessage('显示物资量')
--- fragment #5 ---
WhenReceiveMessage('关闭物资箱')
--- fragment #6 ---
WhenReceiveMessage('显示结果')
--- fragment #7 ---
GotoPosition3D('1652', '2026', '-1')
PointInDirection({}, '78')
SetSize({}, '60')
Show({})
--- fragment #8 ---
WaitSeconds('0.5')
SetSize({}, '50')
GotoTarget('水晶方块')
--- fragment #9 ---
WaitSeconds('0.8')
IfElse(  IsEqual(    Variable('cid'), {}, '1'))
  SaySeconds('物资准备已完成！开始清点0~9号物资箱', '2')
else:
  SaySeconds('物资准备已完成！抽查2~5号物资箱', '2')
--- fragment #10 ---
PlayAnimation('chumo')
--- fragment #11 ---
RunToTargetAndWait('水晶方块')
PlayAnimation('chumo')
PointInDirection({}, '-66')
WaitSeconds('0.5')
PlayAnimation('idle')
--- fragment #12 ---
WaitSeconds('0.2')
PlayAnimation('idle')
--- fragment #13 ---
IfElse(  IsEqual(    Variable('cid'), {}, '3'))
  If(    IsEqual(      Variable('i'), {}, '2'))
    SaySeconds('20>10，充足！', '1.3')
  If(    IsEqual(      Variable('i'), {}, '3'))
    SaySeconds('5<10，需要补充物资！', '1.3')
else:
  If(    IsEqual(      Variable('i'), {}, '0'))
    SaySeconds('12>10，充足！', '1.3')
  If(    IsEqual(      Variable('i'), {}, '1'))
    SaySeconds('8<10，需要补充物资！', '1.3')
  If(    IsEqual(      Variable('i'), {}, '2'))
    SaySeconds('15>10，充足！', '1.3')
  If(    IsEqual(      Variable('i'), {}, '3'))
    SaySeconds('20>10，充足！', '1.3')
  If(    IsEqual(      Variable('i'), {}, '4'))
    SaySeconds('5<10，需要补充物资！', '1.3')

### scene/水晶方块/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  IfElse(    IsEqual(      Variable('cid'), {}, '1'))
    GotoPosition3D('1740', '1915', '-5')
  else:
    GotoPosition3D('1740',       Add('1910', {},         Multiply('2', {}, '30')), '-6')
  PointInDirection({}, '90')
  SetSize({}, '100')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('关闭物资箱')
  IfElse(    IsEqual(      Variable('cid'), {}, '1'))
    GotoPosition3D('1740',       Add('1915', {},         Multiply(          Variable('i'), {}, '30')), '-6')
  else:
    GotoPosition3D('1740',       Add('1910', {},         Multiply(          Variable('i'), {}, '30')), '-6')
  PointInDirection({}, '90')
  SetSize({}, '100')
  Hide({})

### scene/0号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/1号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/2号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/3号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/4号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/5号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/6号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/7号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/8号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/9号/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  Show({})

### scene/九婴体内-绿灯/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  If(    IsEqual(      Variable('cid'), {}, '1'))
    GotoPosition3D('1700', '1930', '2')
  If(    Or(      IsEqual(        Variable('cid'), {}, '2'), {},       IsEqual(        Variable('cid'), {}, '3')))
    GotoPosition3D('1700', '1990', '2')
  PointInDirection({}, '90')
  SetSize({}, '32')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('显示结果')
  WaitSeconds('0.5')
  If(    IsEqual(      Variable('cid'), {}, '1'))
    If(      IsEqual(        Variable('i'), {}, '1'))
      PlaySound('条件成立')
      Show({})
  If(    Or(      IsEqual(        Variable('cid'), {}, '2'), {},       IsEqual(        Variable('cid'), {}, '3')))
    If(      IsEqual(        Variable('i'), {}, '3'))
      PlaySound('条件成立')
      Show({})

### scene/九婴体内-红灯/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1700', '1930', '2')
  PointInDirection({}, '90')
  SetSize({}, '32')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('显示结果')
  WaitSeconds('0.5')
  If(    IsLess(      ListGetItemAt(        Variable('i'), 'cin_cut'), {}, '11'))
    GotoPosition3D('1700',       Add('1930', {},         Multiply('30', {},           Subtract(            Variable('i'), {}, '1'))), '2')
    WaitSeconds('0.3')
    Show({})
    PlayAnimation('闪闪发光特效')
    PlaySound('小核桃收消息3秒版')
    Repeat('3')
      Repeat('5')
        ChangeSize({}, '3')
      Repeat('5')
        ChangeSize({}, '-3')
      WaitSeconds('0.1')

### scene/control/BlockScript [BlockScript] in <BlockScript> (4 fragments)
--- fragment #0 ---
WhenGameStarts()
  SetVar('cid', '2')
  Hide({})
  Forever()
    WaitUntil(      IsEqual(        Variable('state'), {}, '运行'))
    If(      IsEqual(        Variable('cmd'), {}, 'init'))
      e70f5778fcde43e6b28a2fd521505404/myblockdefine()
    If(      IsEqual(        Variable('cmd'), {}, 'finish'))
      BroadcastMessageAndWait('结束判断')
    If(      IsEqual(        Variable('cmd'), {}, 'success'))
      BroadcastMessageAndWait('传递成功')
    If(      IsEqual(        Variable('cmd'), {}, 'fail'))
      BroadcastMessageAndWait('传递失败')
    SetVar('state', '停止')
--- fragment #1 ---
WhenReceiveMessage('结束判断')
  IfElse(    IsEqual(      Variable('*OJ_Judge'), {}, '0'))
    SetVar('err_msg', '代码不正确，修改代码再试试吧。')
    BroadcastMessageAndWait('传递失败')
  else:
    BroadcastMessageAndWait('展示关卡效果')
    BroadcastMessageAndWait('传递成功')
--- fragment #2 ---
WhenReceiveMessage('展示关卡效果')
  SetVar('cid', '2')
  BroadcastMessageAndWait('物资准备')
  BroadcastMessageAndWait('对话')
  BroadcastMessageAndWait('换分镜')
  SetVar('i', '2')
  Repeat('3')
    BroadcastMessageAndWait('跑到位置')
    BroadcastMessageAndWait('打开物资')
    WaitSeconds('0.3')
    BroadcastMessageAndWait('显示物资量')
    IncVar('i', '1')
    BroadcastMessageAndWait('关闭物资箱')
    BroadcastMessageAndWait('显示结果')
--- fragment #3 ---
WhenReceiveMessage('初始化')
  ListDeleteALl('cin_cut')
  ListAdd('12', 'cin_cut')
  ListAdd('8', 'cin_cut')
  ListAdd('15', 'cin_cut')
  ListAdd('20', 'cin_cut')
  ListAdd('5', 'cin_cut')
  ListAdd('18', 'cin_cut')
  ListAdd('30', 'cin_cut')
  ListAdd('25', 'cin_cut')
  ListAdd('10', 'cin_cut')
  ListAdd('22', 'cin_cut')

### scene/九婴体内-绿灯 2/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1700', '2020', '2')
  PointInDirection({}, '90')
  SetSize({}, '32')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('显示结果')
  If(    IsEqual(      Variable('cid'), {}, '2'))
    If(      IsEqual(        Variable('i'), {}, '4'))
      WaitSeconds('0.5')
      PlaySound('条件成立')
      Show({})

### scene/小核桃/BlockScript [BlockScript] in <BlockScript> (10 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1652', '2026', '-1')
  PointInDirection({}, '78')
  SetSize({}, '80')
  Show({})
--- fragment #1 ---
WhenReceiveMessage('对话')
  WaitSeconds('0.8')
  IfElse(    IsEqual(      Variable('cid'), {}, '1'))
    SaySeconds('物资准备已完成！开始清点0~9号物资箱', '2')
  else:
    SaySeconds('物资准备已完成！抽查2~5号物资箱', '2')
--- fragment #2 ---
WhenReceiveMessage('换分镜')
  WaitSeconds('0.5')
  SetSize({}, '70')
  GotoTarget('水晶方块')
--- fragment #3 ---
WhenReceiveMessage('打开物资')
  PlayAnimation('dichudongxi')
  WaitSeconds('0.5')
  PlayAnimation('idle')
--- fragment #4 ---
WhenReceiveMessage('显示物资量')
  PlayAnimation('taishou_loop')
  WaitSeconds('0.3')
  PlaySound('传送音效')
  IfElse(    IsEqual(      Variable('cid'), {}, '3'))
    If(      IsEqual(        Variable('i'), {}, '2'))
      SaySeconds('20>10，充足！', '1.3')
    If(      IsEqual(        Variable('i'), {}, '3'))
      SaySeconds('5<10，需要补充物资！', '1.3')
  else:
    If(      IsEqual(        Variable('i'), {}, '0'))
      SaySeconds('12>10，充足！', '1.3')
    If(      IsEqual(        Variable('i'), {}, '1'))
      SaySeconds('8<10，需要补充物资！', '1.3')
    If(      IsEqual(        Variable('i'), {}, '2'))
      SaySeconds('15>10，充足！', '1.3')
    If(      IsEqual(        Variable('i'), {}, '3'))
      SaySeconds('20>10，充足！', '1.3')
    If(      IsEqual(        Variable('i'), {}, '4'))
      SaySeconds('5<10，需要补充物资！', '1.3')
--- fragment #5 ---
WhenReceiveMessage('关闭物资箱')
  PlayAnimation('dichudongxi')
--- fragment #6 ---
WhenReceiveMessage('显示结果')
  IfElse(    IsEqual(      Variable('cid'), {}, '3'))
    If(      IsEqual(        Variable('i'), {}, '3'))
      WaitSeconds('0.2')
      PlayAnimation('idle')
    If(      IsEqual(        Variable('i'), {}, '4'))
      WaitSeconds('0.2')
      PlayAnimation('dianjishoubi02')
      SaySeconds('物资量：5，紧急补充！', '1.3')
  else:
    If(      IsEqual(        Variable('i'), {}, '1'))
      WaitSeconds('0.2')
      PlayAnimation('idle')
    If(      IsEqual(        Variable('i'), {}, '2'))
      WaitSeconds('0.2')
      PlayAnimation('dianjishoubi02')
      SaySeconds('物资量：8，紧急补充！', '1.3')
    If(      IsEqual(        Variable('i'), {}, '3'))
      WaitSeconds('0.2')
      PlayAnimation('idle')
    If(      IsEqual(        Variable('i'), {}, '4'))
      WaitSeconds('0.2')
      PlayAnimation('idle')
    If(      IsEqual(        Variable('i'), {}, '5'))
      WaitSeconds('0.2')
      PlayAnimation('dianjishoubi02')
      SaySeconds('物资量：5，紧急补充！', '1.3')
--- fragment #7 ---
PlayAnimation('saomiao')
--- fragment #8 ---
SaySeconds('15>10，充足！', '1.3')
--- fragment #9 ---
WhenReceiveMessage('跑到位置')
  RunToTargetAndWait('水晶方块')
  PointInDirection({}, '-60')

### scene/空挂点/BlockScript [BlockScript] in <BlockScript> (2 fragments)
--- fragment #0 ---
WhenReceiveMessage('显示物资量')
  GotoPosition3D('1690',     Add('1930', {},       Multiply('30', {},         Variable('i'))), '-6')
  WaitSeconds('0.4')
  PlayAnimation('出库机扫描特效')
--- fragment #1 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1690', '1930', '-6')
  Show({})

### scene/压缩饼干/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1688', '1929', '3')
  PointInDirection({}, '90')
  SetSize({}, '110')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('cid'), {}, '1'))
    GotoPosition3D('1688',       Add('1929', {},         Multiply('30', {},           Variable('i'))), '3')
    WaitSeconds('0.5')
    IfElse(      IsGreator(        ListGetItemAt(          Add(            Variable('i'), {}, '1'), 'cin_cut'), {}, '17'))
      SetSize({}, '130')
    else:
      If(        IsLess(          ListGetItemAt(            Add(              Variable('i'), {}, '1'), 'cin_cut'), {}, '11'))
        SetSize({}, '90')
    Show({})
--- fragment #2 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('cid'), {}, '1'))
    WaitSeconds('0.5')
    Hide({})

### scene/矿泉水/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1688', '1930', '4')
  PointInDirection({}, '180')
  SetSize({}, '100')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('cid'), {}, '2'))
    If(      IsEqual(        Variable('i'), {}, '2'))
      GotoPosition3D('1688', '1997', '3')
      WaitSeconds('0.5')
      SetSize({}, '180')
    If(      IsEqual(        Variable('i'), {}, '3'))
      GotoPosition3D('1688', '2029', '3')
      WaitSeconds('0.5')
      SetSize({}, '220')
    If(      IsEqual(        Variable('i'), {}, '4'))
      GotoPosition3D('1688', '2055', '3')
      WaitSeconds('0.5')
      SetSize({}, '120')
    Show({})
--- fragment #2 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('cid'), {}, '2'))
    WaitSeconds('0.5')
    Hide({})

### scene/标签1/BlockScript [BlockScript] in <BlockScript> (4 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition2D('-215', '-34')
  SetSize({}, '35')
  SetVar('标签克隆', '1')
  Repeat('10')
    CreateCloneOf('myself')
    IncVar('标签克隆', '1')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('物资准备')
  SetControllerState('change', 'white')
  PlaySound('物品出现')
  If(    IsEqual(      Variable('标签克隆'), {}, '1'))
    SetTitle(      ListGetItemAt('1', 'cin_cut'))
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '2'))
    SetTitle(      ListGetItemAt('2', 'cin_cut'))
    GotoPosition2D('-167', '-34')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '3'))
    SetTitle(      ListGetItemAt('3', 'cin_cut'))
    GotoPosition2D('-120', '-35')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '4'))
    SetTitle(      ListGetItemAt('4', 'cin_cut'))
    GotoPosition2D('-72', '-35')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '5'))
    SetTitle(      ListGetItemAt('5', 'cin_cut'))
    GotoPosition2D('-24', '-35')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '6'))
    SetTitle(      ListGetItemAt('6', 'cin_cut'))
    GotoPosition2D('25', '-35')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '7'))
    SetTitle(      ListGetItemAt('7', 'cin_cut'))
    GotoPosition2D('74', '-36')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '8'))
    SetTitle(      ListGetItemAt('8', 'cin_cut'))
    GotoPosition2D('122', '-36')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '9'))
    SetTitle(      ListGetItemAt('9', 'cin_cut'))
    GotoPosition2D('171', '-36')
    Show({})
  If(    IsEqual(      Variable('标签克隆'), {}, '10'))
    SetTitle(      ListGetItemAt('10', 'cin_cut'))
    GotoPosition2D('220', '-37')
    Show({})
  WaitSeconds('1.2')
  PlaySound('消失')
  Repeat('4')
    ChangeSize({}, '2')
  Repeat('5')
    ChangeSize({}, '-5')
  Hide({})
--- fragment #2 ---
SetSize({}, '50')
--- fragment #3 ---
WaitSeconds('0.2')

### scene/物资标签/BlockScript [BlockScript] in <BlockScript> (12 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  SetControllerState('change', 'white')
  SetSize({}, '50')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('打开物资')
  WaitSeconds('0.3')
  PlaySound('物品出现')
  SetTitle(    ListGetItemAt(      Add(        Variable('i'), {}, '1'), 'cin_cut'))
  If(    IsEqual(      Variable('cid'), {}, '1'))
    If(      IsEqual(        Variable('i'), {}, '0'))
      GotoPosition2D('-116', '-18')
    If(      IsEqual(        Variable('i'), {}, '1'))
      GotoPosition2D('-30', '-18')
  If(    IsEqual(      Variable('cid'), {}, '2'))
    If(      IsEqual(        Variable('i'), {}, '2'))
      GotoPosition2D('-68', '-17')
    If(      IsEqual(        Variable('i'), {}, '3'))
      GotoPosition2D('19', '-17')
    If(      IsEqual(        Variable('i'), {}, '4'))
      GotoPosition2D('104', '-17')
  If(    IsEqual(      Variable('cid'), {}, '3'))
    If(      IsEqual(        Variable('i'), {}, '2'))
      GotoPosition2D('-68', '-17')
    If(      IsEqual(        Variable('i'), {}, '3'))
      GotoPosition2D('19', '-17')
  Show({})
--- fragment #2 ---
WhenReceiveMessage('显示结果')
  WaitSeconds('0.2')
  PlaySound('消失')
  Repeat('4')
    ChangeSize({}, '2')
  Repeat('5')
    ChangeSize({}, '-5')
  Hide({})
  SetSize({}, '50')
--- fragment #3 ---
GotoPosition2D('-134', '-18')
--- fragment #4 ---
GotoPosition2D('-47', '-17')
--- fragment #5 ---
GotoPosition2D('-134', '-18')
--- fragment #6 ---
GotoPosition2D('-47', '-17')
--- fragment #7 ---
GotoPosition2D('-78', '-17')
--- fragment #8 ---
GotoPosition2D('8', '-17')
--- fragment #9 ---
GotoPosition2D('94', '-17')
--- fragment #10 ---
GotoPosition2D('-78', '-17')
--- fragment #11 ---
GotoPosition2D('8', '-17')

### scene/医药包/BlockScript [BlockScript] in <BlockScript> (3 fragments)
--- fragment #0 ---
WhenReceiveMessage('初始化')
  GotoPosition3D('1698', '1930', '-2')
  PointInDirection({}, '90')
  SetSize({}, '85')
  Hide({})
--- fragment #1 ---
WhenReceiveMessage('打开物资')
  If(    IsEqual(      Variable('cid'), {}, '3'))
    GotoPosition3D('1698',       Add('1930', {},         Multiply('30', {},           Variable('i'))), '-2')
    WaitSeconds('0.5')
    IfElse(      IsGreator(        ListGetItemAt(          Add(            Variable('i'), {}, '1'), 'cin_cut'), {}, '17'))
      SetSize({}, '90')
    else:
      If(        IsLess(          ListGetItemAt(            Add(              Variable('i'), {}, '1'), 'cin_cut'), {}, '11'))
        SetSize({}, '65')
    Show({})
--- fragment #2 ---
WhenReceiveMessage('关闭物资箱')
  If(    IsEqual(      Variable('cid'), {}, '3'))
    WaitSeconds('0.5')
    Hide({})