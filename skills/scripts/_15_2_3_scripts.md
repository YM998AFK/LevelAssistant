# 15-2 关卡3 脚本 dump

主 ws: 参考-extracted\15-2 关卡3\e7ace109-c25c-42d6-ad99-1676e078485d.ws


## scene.children[0](services).children[2](Camera).children[0](BlockScript)  id=528b219ba4

frags 数量: 4


### frag[0]  define=WhenGameStarts
```
WhenGameStarts()
```

### frag[1]  define=SetCameraFOV
```
SetCameraFOV('25')
PointInDirection(<None>, '-90')
PointInPitch(<None>, '125')
CameraFollow('计数机器人', '640', '0', '500')
```

### frag[2]  define=SetCameraFOV
```
SetCameraFOV('25')
PointInDirection(<None>, '-90')
PointInPitch(<None>, '125')
CameraFollow('计数机器人', '200', '0', '150')
```

### frag[3]  define=6377b110e62644a28570625c30d5c6ad/myblockdefine
```
6377b110e62644a28570625c30d5c6ad/myblockdefine()
```

## scene.children[5](计数机器人).children[0](BlockScript)  id=1d9c30454f

frags 数量: 5


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition3D('-2755', '87', '654')
  PointInDirection(<None>, '90')
  Show(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('机器人左转')
  TurnLeft(<None>, '90')
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('角色升级')
  PlayAnimationUntil('避雷针塔升级特效')
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('机器人右转')
  TurnRight(<None>, '90')
```

### frag[4]  define=WhenReceiveMessage
```
WhenReceiveMessage('机器人走到大门前')
  TurnRight(<None>, '90')
```

## scene.children[6](矿洞大门).children[0](BlockScript)  id=938c9620ce

frags 数量: 2


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition3D('-2850', '-141', '657')
  Show(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('大门打开')
  PlayAnimationUntil('kaimen')
```

## scene.children[7](空挂点).children[0](BlockScript)  id=96fde2601c

frags 数量: 4


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('judge')
  SetVar('输入元素', '')
  SetVar('n', '0')
  ListDeleteALl('cin_cut')
  Repeat((StrLength((Variable('*OJ-输入信息')))))
    IncVar('n', '1')
    IfElse((Or((IsEqual((StrLetterOf((Variable('n')), (Variable('*OJ-输入信息')))), <None>, ' ')), <None>, (IsEqual((StrLetterOf((Variable('n')), (Variable('*OJ-输入信息')))), <None>, '§')))))
      If((Not((IsEqual((Variable('输入元素')), <None>, '')))))
        ListAdd((Variable('输入元素')), 'cin_cut')
        SetVar('输入元素', '')
      SetVar('输入元素', (StrJoin((Variable('输入元素')), (StrLetterOf((Variable('n')), (Variable('*OJ-输入信息')))))))
      If((IsEqual((Variable('n')), <None>, (StrLength((Variable('*OJ-输入信息')))))))
        ListAdd((Variable('输入元素')), 'cin_cut')
        SetVar('输入元素', '')
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('judge')
  ListDeleteALl('cout_cut')
  SetVar('输出结果', '')
  SetVar('输出元素', '')
  SetVar('n1', '0')
  SetVar('space-flag', '0')
  SetVar('endl_flag', '0')
  SetVar('换行符', '')
  Repeat((StrLength((Variable('*OJ-执行结果')))))
    IncVar('n1', '1')
    IfElse((IsEqual((StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))), <None>, '§')))
      If((Not((IsEqual((Variable('space-flag')), <None>, '1')))))
        SetVar('输出元素', '')
      SetVar('换行符', (StrJoin((Variable('换行符')), '§')))
      IncVar('space-flag', '1')
      SetVar('输出元素', (StrJoin((Variable('输出元素')), (StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))))))
    If((And((Not((IsEqual((StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))), <None>, ' ')))), <None>, (Not((IsEqual((StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))), <None>, '§')))))))
      SetVar('输出结果', (StrJoin((Variable('输出结果')), (Variable('换行符')))))
      SetVar('换行符', '')
      SetVar('输出结果', (StrJoin((Variable('输出结果')), (Variable('输出元素')))))
      SetVar('输出元素', '')
      SetVar('space-flag', '0')
  BroadcastMessageAndWait('cout_judge2')
```

### frag[2]  define=WhenStartup
```
WhenStartup()
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('cout_judge2')
  SetVar('输出元素', '')
  SetVar('n1', '0')
  SetVar('space-flag', '1')
  Repeat((StrLength((Variable('*OJ-执行结果')))))
    IncVar('n1', '1')
    IfElse((Or((IsEqual((StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))), <None>, ' ')), <None>, (IsEqual((StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))), <None>, '§')))))
      If((Not((IsEqual((Variable('输出元素')), <None>, '')))))
        ListAdd((Variable('输出元素')), 'cout_cut')
        SetVar('输出元素', '')
      SetVar('输出元素', (StrJoin((Variable('输出元素')), (StrLetterOf((Variable('n1')), (Variable('*OJ-执行结果')))))))
      If((IsEqual((Variable('n')), <None>, (StrLength((Variable('*OJ-执行结果')))))))
        ListAdd((Variable('输出元素')), 'cout_cut')
        SetVar('输出元素', '')
```

## scene.children[8](control).children[0](BlockScript)  id=87bce9bbbd

frags 数量: 8


### frag[0]  define=WhenGameStarts
```
WhenGameStarts()
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('运行')
  If((IsEqual((Variable('cmd')), <None>, 'init')))
    87bce9bbbd684bf285c11c5401f851bd/myblockdefine()
    BroadcastMessageAndWait('初始化')
    BroadcastMessageAndWait('judge')
  If((IsEqual((Variable('cmd')), <None>, 'cintest')))
    BroadcastMessageAndWait('cin判断')
  If((IsEqual((Variable('cmd')), <None>, 'couttest')))
    BroadcastMessageAndWait('cout判断')
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('cin判断')
  If((IsLess((ListGetItemAt('1', 'cin_cut')), <None>, '1')))
    SetVar('err_msg', '输入的值需要大于等于1哦')
    BroadcastMessageAndWait('传递失败')
```

### frag[3]  define=WhenStartup
```
WhenStartup()
  SetVar('*OJ-输入信息', '')
  SetVar('*OJ-执行结果', '')
  SetVar('err_msg', '')
  SetVar('cmd', '')
  SetVar('state', '停止')
  BroadcastMessageAndWait('初始化')
```

### frag[4]  define=WhenReceiveMessage
```
WhenReceiveMessage('cout判断')
```

### frag[5]  define=WhenGameStarts
```
WhenGameStarts()
  SetVar('*OJ-Judge', '1')
  ListAdd('50', 'cin_cut')
  If((IsEqual((Variable('*OJ-Judge')), <None>, '0')))
    SetVar('err_msg', '代码不正确，再试试吧')
    BroadcastMessageAndWait('传递失败')
  If((IsEqual((Variable('*OJ-Judge')), <None>, '1')))
    IfElse((And((IsGreator((ListGetItemAt('1', 'cin_cut')), <None>, '0')), <None>, (IsLess((ListGetItemAt('1', 'cin_cut')), <None>, '11')))))
      BroadcastMessageAndWait('初始化')
      BroadcastMessageAndWait('准备')
      BroadcastMessageAndWait('机器人左转')
      BroadcastMessageAndWait('机器人发射')
      WaitSeconds('0.5')
      Repeat((ListGetItemAt('1', 'cin_cut')))
        BroadcastMessageAndWait('屏幕显示')
        BroadcastMessageAndWait('计算')
        If((IsLess((Variable('关卡i')), <None>, (ListGetItemAt('1', 'cin_cut')))))
          BroadcastMessageAndWait('+1')
        IncVar('关卡i', '1')
      BroadcastMessageAndWait('收起')
      BroadcastMessageAndWait('机器人右转')
      BroadcastMessageAndWait('生成成长树')
      WaitSeconds('1')
      BroadcastMessageAndWait('收起成长树')
      BroadcastMessageAndWait('机器人右转')
      BroadcastMessageAndWait('机器人开门')
      BroadcastMessageAndWait('大门打开')
      BroadcastMessageAndWait('大门特效')
      BroadcastMessageAndWait('初始化')
      BroadcastMessageAndWait('准备')
      BroadcastMessageAndWait('机器人左转')
      BroadcastMessageAndWait('机器人发射')
      BroadcastMessageAndWait('单独判断')
      WaitSeconds('0.5')
      Repeat('10')
        BroadcastMessageAndWait('屏幕显示')
        BroadcastMessageAndWait('计算')
        If((IsLess((Variable('关卡i')), <None>, '10')))
          BroadcastMessageAndWait('+1')
        IncVar('关卡i', '1')
      BroadcastMessageAndWait('密码雨')
      BroadcastMessageAndWait('收起')
      BroadcastMessageAndWait('机器人右转')
      BroadcastMessageAndWait('生成成长树')
      WaitSeconds('1')
      BroadcastMessageAndWait('收起成长树')
      BroadcastMessageAndWait('机器人右转')
      BroadcastMessageAndWait('机器人开门')
      BroadcastMessageAndWait('大门打开')
      BroadcastMessageAndWait('大门特效')
```

### frag[6]  define=WaitSeconds
```
WaitSeconds('1')
If((IsEqual((Variable('*OJ-输入信息')), <None>, '')))
  SetVar('err_msg', '需要先输入测试样例，再点击运行哦')
  BroadcastMessageAndWait('传递失败')
WaitUntil((Not((And((IsEqual((Variable('*OJ-执行结果')), <None>, '')), <None>, (IsEqual((Variable('*OJ-输入信息')), <None>, '')))))))
SetVar('cmd', 'init')
BroadcastMessageAndWait('运行')
SetVar('cmd', 'cintest')
BroadcastMessageAndWait('运行')
SetVar('cmd', 'couttest')
BroadcastMessageAndWait('运行')
```

### frag[7]  define=ListAdd
```
ListAdd('4', 'cin_cut')
ListAdd('6', 'cin_cut')
ListAdd('23', 'cin_cut')
ListAdd('6', 'cin_cut')
```

## scene.children[9](空挂点 3).children[0](BlockScript)  id=47798a5e2b

frags 数量: 3


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition3D('-2231', '96', '886')
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('机器人发射')
  PlayAnimation('一辆半挂魔法')
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('屏幕显示')
  StopAnimation('一辆半挂魔法')
```

## scene.children[10](LabelBubble(5).Basic).children[0](BlockScript)  id=43d437eb4e

frags 数量: 4


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('111', '28')
  SetVar('关卡n', (ListGetItemAt('1', 'cin_cut')))
  SetTitle((StrJoin('循环次数：', (Variable('关卡n')))))
  SetSize(<None>, '60')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('屏幕显示')
  Show(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('密码雨')
  Hide(<None>)
```

## scene.children[11](避雷针操作界面).children[1](BlockScript)  id=bf2ee097e3

frags 数量: 4


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('115', '-69')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('屏幕显示')
  Show(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

## scene.children[12](Screen Text.Basic).children[0](BlockScript)  id=a215176bd5

frags 数量: 5


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('114', '-17')
  SetVar('关卡i', '1')
  SetTitle((StrJoin('i：', (Variable('关卡i')))))
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('屏幕显示')
  SetTitle((StrJoin('i：', (Variable('关卡i')))))
  Show(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('角色升级')
  Repeat('2')
    Repeat('10')
      ChangeSize(<None>, '3')
    WaitSeconds('0.1')
    Repeat('10')
      ChangeSize(<None>, '-3')
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

### frag[4]  define=WhenReceiveMessage
```
WhenReceiveMessage('密码雨')
  Hide(<None>)
```

## scene.children[13](Button1.Basic).children[0](BlockScript)  id=9590627e17

frags 数量: 4


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('计算')
  SetTitle((StrJoin((Variable('关卡i')), '%5==0')))
  Show(<None>)
  WaitSeconds('0.5')
  BroadcastMessageAndWait('判断')
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('密码雨')
  Hide(<None>)
```

## scene.children[14](对勾).children[1](BlockScript)  id=21b23be532

frags 数量: 5


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  Hide(<None>)
  ListDeleteALl('角色升级')
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('判断')
  IfElse((And((IsGreator((ListGetItemAt('1', 'cin_cut')), <None>, '0')), <None>, (IsLess((ListGetItemAt('1', 'cin_cut')), <None>, '11')))))
    If((IsEqual((Mod((Variable('关卡i')), '5')), <None>, '0')))
      Show(<None>)
      WaitSeconds('0.5')
      Hide(<None>)
      ListAdd((Variable('关卡i')), '角色升级')
      BroadcastMessageAndWait('角色升级')
    If((IsEqual((Mod((Variable('关卡i')), '5')), <None>, '0')))
      Show(<None>)
      WaitSeconds('0.5')
      Hide(<None>)
      BroadcastMessageAndWait('角色升级')
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('单独判断')
  SetVar('单独判断_i', '1')
  Repeat((ListGetItemAt('1', 'cin_cut')))
    If((IsEqual((Mod((Variable('单独判断_i')), '5')), <None>, '0')))
      ListAdd((Variable('单独判断_i')), '角色升级')
    IncVar('单独判断_i', '1')
```

### frag[4]  define=BroadcastMessageAndWait
```
BroadcastMessageAndWait('单独判断')
```

## scene.children[15](叉).children[1](BlockScript)  id=89fb4c1a45

frags 数量: 3


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('判断')
  If((Not((IsEqual((Mod((Variable('关卡i')), '5')), <None>, '0')))))
    Show(<None>)
    WaitSeconds('0.2')
    Hide(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

## scene.children[16](CoinPlus-MinusValue(1).Basic).children[0](BlockScript)  id=80cd9c3537

frags 数量: 3


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  SetChildStringProperty('n18', 'title', '+1')
  SetSize(<None>, '75')
  GotoPosition2D('141', '-11')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('+1')
  GotoPosition2D('141', '-11')
  Show(<None>)
  GlideSecsToPosition2D('0.3', '160', '1')
  Hide(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起')
  Hide(<None>)
```

## scene.children[17](讲解框800x 2).children[1](BlockScript)  id=a1f07878ad

frags 数量: 3


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('134', '-12')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('生成成长树')
  Show(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起成长树')
  Hide(<None>)
```

## scene.children[18](社牛水晶球图片).children[1](BlockScript)  id=7bb45b9a40

frags 数量: 5


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('109', '-13')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('生成成长树')
  IfElse((Or((IsLess((ListGetLength('角色升级')), <None>, '6')), <None>, (IsEqual((ListGetLength('角色升级')), <None>, '6')))))
    ChangePosY(<None>, (Multiply('37', <None>, (MathFunc('floor', (Divide((ListGetLength('角色升级')), <None>, '2')))))))
    Repeat((ListGetLength('角色升级')))
      CreateCloneOf('myself')
      ChangePosY(<None>, '-37')
    ChangePosY(<None>, (Multiply('37', <None>, '3')))
    Repeat('3')
      CreateCloneOf('myself')
      ChangePosY(<None>, '-37')
    BroadcastMessageAndWait('...')
    GotoPosition2D('109', '-81')
    Repeat('2')
      CreateCloneOf('myself')
      ChangePosY(<None>, '-37')
```

### frag[2]  define=WhenIStartAsAClone
```
WhenIStartAsAClone()
  Show(<None>)
```

### frag[3]  define=ListGetLength
```
ListGetLength('角色升级')
```

### frag[4]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起成长树')
  Hide(<None>)
```

## scene.children[19](LabelBuubble(6).Basic).children[0](BlockScript)  id=9572e68942

frags 数量: 4


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('146', '-10')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('生成成长树')
  IfElse((Or((IsLess((ListGetLength('角色升级')), <None>, '6')), <None>, (IsEqual((ListGetLength('角色升级')), <None>, '6')))))
    ChangePosY(<None>, (Multiply('37', <None>, (MathFunc('floor', (Divide((ListGetLength('角色升级')), <None>, '2')))))))
    SetVar('升级_i', '1')
    Repeat((ListGetLength('角色升级')))
      SetTitle((ListGetItemAt((Variable('升级_i')), '角色升级')))
      CreateCloneOf('myself')
      ChangePosY(<None>, '-40')
      IncVar('升级_i', '1')
    ChangePosY(<None>, (Multiply('37', <None>, '3')))
    SetVar('升级_i', '1')
    Repeat('3')
      SetTitle((ListGetItemAt((Variable('升级_i')), '角色升级')))
      CreateCloneOf('myself')
      ChangePosY(<None>, '-40')
      IncVar('升级_i', '1')
    GotoPosition2D('146', '-78')
    SetTitle((ListGetItemAt((Subtract((ListGetLength('角色升级')), <None>, '1')), '角色升级')))
    CreateCloneOf('myself')
    ChangePosY(<None>, '-40')
    SetTitle((ListGetItemAt((ListGetLength('角色升级')), '角色升级')))
    CreateCloneOf('myself')
    ChangePosY(<None>, '-40')
```

### frag[2]  define=WhenIStartAsAClone
```
WhenIStartAsAClone()
  Show(<None>)
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起成长树')
  Hide(<None>)
```

## scene.children[20](箭头).children[6](BlockScript)  id=6dee9a0686

frags 数量: 4


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('145', '-30')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('生成成长树')
  IfElse((Or((IsLess((ListGetLength('角色升级')), <None>, '6')), <None>, (IsEqual((ListGetLength('角色升级')), <None>, '6')))))
    ChangePosY(<None>, (Multiply('37', <None>, (MathFunc('floor', (Divide((ListGetLength('角色升级')), <None>, '2')))))))
    Repeat((Subtract((ListGetLength('角色升级')), <None>, '1')))
      CreateCloneOf('myself')
      ChangePosY(<None>, '-40')
    ChangePosY(<None>, (Multiply('37', <None>, '3')))
    Repeat('3')
      CreateCloneOf('myself')
      ChangePosY(<None>, '-40')
    GotoPosition2D('145', '-98')
    CreateCloneOf('myself')
    ChangePosY(<None>, '-40')
```

### frag[2]  define=WhenIStartAsAClone
```
WhenIStartAsAClone()
  Show(<None>)
```

### frag[3]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起成长树')
  Hide(<None>)
```

## scene.children[21](空挂点 2).children[0](BlockScript)  id=0544e143c0

frags 数量: 2


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition3D('-1316', '-57', '1071')
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('密码雨')
  SetAnimationSpeed('15')
  PlayAnimation('代码化')
  WaitSeconds('2.5')
  StopAnimation('代码化')
```

## scene.children[22](LabelBubblenobg.Basic).children[0](BlockScript)  id=fa415bb9ac

frags 数量: 3


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition2D('130', '-26')
  Hide(<None>)
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('...')
  Show(<None>)
```

### frag[2]  define=WhenReceiveMessage
```
WhenReceiveMessage('收起成长树')
  Hide(<None>)
```

## scene.children[23](空挂点 4).children[0](BlockScript)  id=3261fb7fb5

frags 数量: 2


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition3D('-1771', '-103', '962')
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('机器人开门')
  PlayAnimation('rhand机甲扫描')
  WaitSeconds('1.5')
  StopAnimation('rhand机甲扫描')
```

## scene.children[24](空挂点 5).children[0](BlockScript)  id=ddcce56c17

frags 数量: 2


### frag[0]  define=WhenReceiveMessage
```
WhenReceiveMessage('初始化')
  GotoPosition3D('-1452', '-140', '1035')
```

### frag[1]  define=WhenReceiveMessage
```
WhenReceiveMessage('大门特效')
  PlayAnimation('密室大门穿越特效')
  WaitSeconds('1')
  StopAnimation('密室大门穿越特效')
```


## scene.props2 keys
```
variable = {"type": "Simple", "value": "0"}
#EVENT = {"type": "SimpleList", "value": ["CMD_NewMessage", "judge", "cout_judge2", "传递失败", "运行", "初始化", "cin判断", "cout判断", "准备", "机器人左转", "机器人发射", "屏幕显示", "计算", "判断", "+1", "角色升级", "收起", "机器人右转", "生成成长树", "密码雨", "...", "单独判断", "收起成长树", "机器人走到大门前", "大门打开", "机器人开门", "大门特效"]}
*OJ-输入信息 = {"type": "Simple", "value": "0"}
*OJ-执行结果 = {"type": "Simple", "value": "0"}
cin_cut = {"type": "SimpleList", "value": []}
cout_cut = {"type": "SimpleList", "value": []}
errMsg = {"type": "Simple", "value": "0"}
结果 = {"type": "Simple", "value": "0"}
输入元素 = {"type": "Simple", "value": "0"}
n = {"type": "Simple", "value": "0"}
输出结果 = {"type": "Simple", "value": "0"}
输出元素 = {"type": "Simple", "value": "0"}
n1 = {"type": "Simple", "value": "0"}
space-flag = {"type": "Simple", "value": "0"}
endl_flag = {"type": "Simple", "value": "0"}
换行符 = {"type": "Simple", "value": "0"}
err_msg = {"type": "Simple", "value": "0"}
cmd = {"type": "Simple", "value": "0"}
i_control = {"type": "Simple", "value": "0"}
state = {"type": "Simple", "value": "0"}
*OJ-Judge = {"type": "Simple", "value": "0"}
关卡n = {"type": "Simple", "value": "0"}
关卡i = {"type": "Simple", "value": "0"}
角色升级 = {"type": "SimpleList", "value": []}
升级_i = {"type": "Simple", "value": "0"}
单独判断_i = {"type": "Simple", "value": "0"}
```