#include <AccelStepper.h>
#include <SoftwareSerial.h>

SoftwareSerial mySerial(11, 12); //定义蓝牙串口
//需要步距角的测定
const int x_step = 1006;
const int y_step = 778;

const int borderx = 0; //x轴的边界最大值
const int bordery = 0; //y轴的边界最大值

const int enablePin = 8;

const int xdirPin = 5; //1号电机
const int xstepPin = 2;
const int ydirPin = 6; //2号电机
const int ystepPin = 3;

AccelStepper stepper1(1, xstepPin, xdirPin);
AccelStepper stepper2(1, ystepPin, ydirPin);

//Gcode方面能够实现的函数分别是
//1.G0/G1任意两点之间的直线移动
//2.G2/G3圆弧移动，通常是圆移动
//3.G4暂停移动
//4.G28归零
//5.G92设定当前的初始位置
//6.M201/M202设定最大加速度
//7.M220设置速度

void setup()
{

  mySerial.begin(38400);
  Serial.begin(38400);

  pinMode(xstepPin, OUTPUT);
  pinMode(xdirPin, OUTPUT);
  pinMode(ystepPin, OUTPUT);
  pinMode(ydirPin, OUTPUT);
  pinMode(enablePin, OUTPUT);

  digitalWrite(enablePin, LOW);

  //分别设定最大速度与加速度
  stepper1.setMaxSpeed(300.0);
  stepper1.setAcceleration(100.0);
  stepper2.setMaxSpeed(300.0);
  stepper2.setAcceleration(100.0);
}

//这样还能忘，封装成函数
void stepper_xplus(int step1, int step2)
{ //x正方向移动
  while (1)
  {
    stepper1.moveTo(step1);
    stepper2.moveTo(step2);
    if (stepper1.currentPosition() == step1)
    { //在这个时候一定要将当前位置设置为0
      stepper1.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      break;
    }
    stepper1.run();
    stepper2.run();
  }
}

void stepper_xminus(int step1, int step2)
{ //x负方向移动
  while (1)
  {
    stepper1.moveTo(-step1);
    stepper2.moveTo(-step2);
    if (stepper1.currentPosition() == -step1)
    {
      stepper1.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      break;
    }
    stepper1.run();
    stepper2.run();
  }
}

void stepper_yplus(int step1, int step2)
{ //y正方向移动
  while (1)
  {
    stepper1.moveTo(-step1);
    stepper2.moveTo(step2);
    if (stepper1.currentPosition() == -step1)
    {
      stepper1.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      break;
    }
    stepper1.run();
    stepper2.run();
  }
}

void stepper_yminus(int step1, int step2)
{ //y负方向移动
  while (1)
  {
    stepper1.moveTo(step1);
    stepper2.moveTo(-step2);
    if (stepper1.currentPosition() == step1)
    {
      stepper1.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      break;
    }
    stepper1.run();
    stepper2.run();
  }
}

void array_move(int column, int row)
{ //阵列移动，蛇形，一定要从右上角开始
  int i, j;
  delay(1000);

  for (i = 0; i < column; i++)
  {
    if (i % 2 == 0)
    {
      for (j = 0; j < row - 1; j++)
      {
        stepper_xplus(x_step, x_step);
        delay(10000);
      }
    }
    else
    {
      for (j = 0; j < row - 1; j++)
      {
        stepper_xminus(x_step, x_step);
        delay(10000);
      }
    }

    stepper_yminus(y_step, y_step);
    delay(10000);
  }
  delay(100000);
}

void loop()
{
  //  array_move(4,3);
  //    delay(20000);
  //    stepper_yminus(y_step,y_step);
  //    delay(25000);
  //    stepper_yminus(y_step,y_step);
  //    delay(25000);
  //    stepper_yminus(y_step,y_step);
  //    delay(5000);
}

void loop()
{ //将这个版本改装成为grbl中的代码录入的格式
  if (Serial.available())
  {
    digitalWrite(enablePin, LOW);
    mySerial.write(Serial.read());
  }

  while (mySerial.available())
  {                                    //可以一次性输入多条指令，进行持续工作
    char serialData = mySerial.read(); //这是读取一个字符的意思，但是如果需要解析一串字符，便需要进行文本解析
    while (serialData != '\n')
    { //当不等于换行符时，便一直接受，确保能够收到相应的数据，第一个字符代表移动方向，第二数字代表移动距离
      //而第一个代表方向的字符已经接受到了，因此现在只需要接收代表距离的字符
    }

    if ('f' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Xplus Command.");
      stepper_xplus(x_step, x_step);
      delay(10000);
    }

    else if ('b' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Xminus Command.");
      stepper_xminus(x_step, x_step);
      delay(10000);
    }

    else if ('l' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Yplus Command.");
      stepper_yplus(y_step, y_step);
      delay(10000);
    }

    else if ('r' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Yminus Command.");
      stepper_yminus(y_step, y_step);
      delay(10000);
    }

    else if ('s' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Stop!");
      digitalWrite(enablePin, HIGH); //直接写使能关停
    }
  }
}

//通信版本
void loop()
{ //属于另一个通信版本
  if (Serial.available())
  {
    digitalWrite(enablePin, LOW);
    mySerial.write(Serial.read());
  }

  if (mySerial.available())
  {

    char serialData = mySerial.read(); //读出来一个字符

    if ('f' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Forward Command.");
      stepper1.move(2000);
      stepper2.move(2000);
    }

    else if ('b' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Backward Command.");
      stepper1.move(2000);
      stepper2.move(-2000);
    }

    else if ('l' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Leftturn Command.");
      stepper1.move(-2000);
      stepper1.move(2000);
    }

    else if ('r' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Rightturn Command.");
      stepper1.move(-2000);
      stepper2.move(-2000);
    }

    else if ('s' == serialData)
    {
      Serial.print(serialData);
      Serial.println("Stop!");
      digitalWrite(enablePin, HIGH);
    }
  }

  stepper1.run();
  stepper2.run();
}