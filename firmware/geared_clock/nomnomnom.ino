/* Piranha Clock V6: Arduino UNO R4 Minima.
 * MG995 geared jaws + MG90S tendon drum. Two positional servos required.
 * Read docs/ELECTRONICS.md. These pulse endpoints are initial calibration
 * values, not measurements of your servo. No automatic motion until ARM.
 */
#include <Servo.h>
#include <Wire.h>
#include <RTC.h>
#include <stdlib.h>
#include <string.h>

constexpr uint8_t SERVO_COUNT = 2;
static_assert(SERVO_COUNT == 2, "This mechanism requires both servos");
constexpr uint8_t JAW_PIN=7, TONGUE_PIN=6, BUZZER_PIN=8, CLK_PIN=3, DIO_PIN=4;
constexpr int JAW_CLOSED_US=1100, JAW_OPEN_US=1656;  // estimate: upper +50, lower -12.5 degrees
constexpr int TONGUE_IN_US=850, TONGUE_OUT_US=2313; // initial estimate: 131.7 degrees
// Servo pulse-to-angle slopes vary. Calibrate UNLOADED before attaching either drive.
// Tongue OUT winds 23.0 mm of underside string onto a 10 mm-radius drum.
// Reverse endpoint order if the purchased servo winds in the wrong direction.
constexpr uint16_t JAW_MS=1200, TONGUE_OUT_MS=900, TONGUE_IN_MS=1200;
// The basic build needs only the board and two servos. Enable extras you fit.
constexpr bool USE_DS3231=false;  // true: external battery-backed clock on I2C
constexpr bool USE_DISPLAY=false; // true: TM1637 four-digit module
constexpr bool USE_BUZZER=false;  // true: low-current passive piezo on D8
constexpr bool AUTO_ARM_AFTER_CALIBRATION=false; // change only after unloaded fitting
constexpr uint8_t QUIET_START=22, QUIET_END=8;
Servo jaw,tongue;
bool armed=false,rtcGood=false,internalClockSet=false,homed=false;
struct Clock { uint16_t year; uint8_t month,day,hour,minute,second; } now;
uint32_t lastHourKey=0xffffffffUL,lastClockRead=0;
enum Stage { IDLE,OPENING,EXTENDING,HOLDING,RETRACTING,CLOSING,RESTING };
Stage stage=IDLE;
uint32_t stageStart=0;
float jawPos=0,tonguePos=0,startJaw=0,startTongue=0;
int repeats=0;
char line[48];uint8_t used=0;bool lineOverflow=false;
uint8_t dec(uint8_t b){return (b>>4)*10+(b&15);}
uint8_t bcd(uint8_t d){return ((d/10)<<4)|(d%10);}
bool readReg(uint8_t r,uint8_t &v){Wire.beginTransmission(0x68);Wire.write(r);if(Wire.endTransmission(false)!=0)return false;if(Wire.requestFrom(0x68,1)!=1)return false;v=Wire.read();return true;}
bool valid(const Clock &c){
  const uint8_t days[]={31,28,31,30,31,30,31,31,30,31,30,31};
  if(c.year<2000||c.year>2099||c.month<1||c.month>12||c.hour>23||c.minute>59||c.second>59)return false;
  uint8_t d=days[c.month-1]+(c.month==2 && c.year%4==0);
  return c.day>=1&&c.day<=d;
}
bool readDS3231(){
  uint8_t status;if(!readReg(0x0f,status)||(status&0x80))return false;
  Wire.beginTransmission(0x68);Wire.write(0);if(Wire.endTransmission(false)!=0)return false;
  if(Wire.requestFrom(0x68,7)!=7)return false;
  now.second=dec(Wire.read()&0x7f);now.minute=dec(Wire.read()&0x7f);
  uint8_t hr=Wire.read();now.hour=(hr&0x40)?(dec(hr&0x1f)%12+((hr&0x20)?12:0)):dec(hr&0x3f);
  Wire.read();now.day=dec(Wire.read()&0x3f);uint8_t mo=Wire.read();now.month=dec(mo&0x1f);now.year=2000+dec(Wire.read());
  return !(mo&0x80)&&valid(now);
}
bool setDS3231(const Clock &c){
  if(!valid(c))return false;
  Wire.beginTransmission(0x68);Wire.write(0);Wire.write(bcd(c.second));Wire.write(bcd(c.minute));Wire.write(bcd(c.hour));Wire.write(1);Wire.write(bcd(c.day));Wire.write(bcd(c.month));Wire.write(bcd(c.year-2000));
  if(Wire.endTransmission()!=0)return false;
  uint8_t st;if(!readReg(0x0f,st))return false;
  Wire.beginTransmission(0x68);Wire.write(0x0f);Wire.write(st&0x7f);
  return Wire.endTransmission()==0;
}
bool readClock(){
  if(USE_DS3231)return readDS3231();
  if(!internalClockSet)return false; // SET explicitly after each reset
  RTCTime t;
  if(!RTC.getTime(t))return false;
  now={(uint16_t)t.getYear(),(uint8_t)Month2int(t.getMonth()),
       (uint8_t)t.getDayOfMonth(),(uint8_t)t.getHour(),
       (uint8_t)t.getMinutes(),(uint8_t)t.getSeconds()};
  return valid(now);
}
bool setClock(const Clock &c){
  if(!valid(c))return false;
  if(USE_DS3231)return setDS3231(c);
  // 2000-01-01 was Saturday; calculate the weekday for the RTC too.
  const uint8_t md[]={31,28,31,30,31,30,31,31,30,31,30,31};
  unsigned days=c.day-1;
  for(unsigned y=2000;y<c.year;y++)days+=365+(y%4==0);
  for(unsigned m=1;m<c.month;m++)days+=md[m-1]+(m==2&&c.year%4==0);
  RTCTime t(c.day,static_cast<Month>(c.month-1),c.year,c.hour,c.minute,c.second,
            static_cast<DayOfWeek>((days+6)%7),SaveLight::SAVING_TIME_INACTIVE);
  internalClockSet=RTC.setTime(t);
  return internalClockSet;
}
// TM1637 open-drain protocol, 4-digit module, adjustable 0..7 brightness.
void dio(bool high){if(high){pinMode(DIO_PIN,INPUT_PULLUP);}else{pinMode(DIO_PIN,OUTPUT);digitalWrite(DIO_PIN,LOW);}}
void startBus(){dio(true);digitalWrite(CLK_PIN,HIGH);delayMicroseconds(3);dio(false);}
void stopBus(){digitalWrite(CLK_PIN,LOW);dio(false);delayMicroseconds(3);digitalWrite(CLK_PIN,HIGH);delayMicroseconds(3);dio(true);}
void sendByte(uint8_t v){for(uint8_t i=0;i<8;i++){digitalWrite(CLK_PIN,LOW);dio(v&1);delayMicroseconds(3);digitalWrite(CLK_PIN,HIGH);delayMicroseconds(3);v>>=1;}digitalWrite(CLK_PIN,LOW);dio(true);delayMicroseconds(3);digitalWrite(CLK_PIN,HIGH);delayMicroseconds(3);digitalWrite(CLK_PIN,LOW);}
void displayClock(){
  if(!USE_DISPLAY)return;
  const uint8_t seg[]={0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f};
  uint8_t a[4]={0x40,0x40,0x40,0x40};
  if(rtcGood){a[0]=seg[now.hour/10];a[1]=seg[now.hour%10]|0x80;a[2]=seg[now.minute/10];a[3]=seg[now.minute%10];}
  startBus();sendByte(0x40);stopBus();startBus();sendByte(0xc0);for(uint8_t s:a)sendByte(s);stopBus();startBus();sendByte(0x8a);stopBus();
}
float ease(float t){t=constrain(t,0,1);return t*t*(3-2*t);}
// Fractions outside 0..1 are allowed only for unloaded calibration, so HOME
// can interpolate smoothly from a manually commanded pulse back to rest.
void moveJaw(float t){jawPos=t;jaw.writeMicroseconds(constrain(int(JAW_CLOSED_US+(JAW_OPEN_US-JAW_CLOSED_US)*t),800,2350));}
void moveTongue(float t){tonguePos=t;tongue.writeMicroseconds(constrain(int(TONGUE_IN_US+(TONGUE_OUT_US-TONGUE_IN_US)*t),800,2350));}
bool attachDrive(Servo &drive,uint8_t pin,int pulse){
  if(!drive.attached())drive.attach(pin,800,2350);
  if(!drive.attached()){Serial.println("Servo attachment failed.");return false;}
  drive.writeMicroseconds(pulse);
  return true;
}
bool attachBoth(){
  bool a=attachDrive(jaw,JAW_PIN,int(JAW_CLOSED_US+(JAW_OPEN_US-JAW_CLOSED_US)*jawPos));
  bool b=attachDrive(tongue,TONGUE_PIN,int(TONGUE_IN_US+(TONGUE_OUT_US-TONGUE_IN_US)*tonguePos));
  return a&&b;
}
void enter(Stage s){stage=s;stageStart=millis();startJaw=jawPos;startTongue=tonguePos;}
void beginCuckoo(int count){if(!armed||!homed||stage!=IDLE)return;homed=false;repeats=constrain(count,1,12);enter(OPENING);}
void motion(){
  uint32_t e=millis()-stageStart;
  switch(stage){
    case IDLE:break;
    case OPENING:moveJaw(startJaw+(1-startJaw)*ease(float(e)/JAW_MS));if(e>=JAW_MS)enter(EXTENDING);break;
    case EXTENDING:moveTongue(startTongue+(1-startTongue)*ease(float(e)/TONGUE_OUT_MS));if(e>=TONGUE_OUT_MS)enter(HOLDING);break;
    case HOLDING:
      if(USE_BUZZER){if(e<140)tone(BUZZER_PIN,880);else if(e<300)tone(BUZZER_PIN,660);else noTone(BUZZER_PIN);}
      if(e>=520)enter(SERVO_COUNT==2?RETRACTING:CLOSING);break;
    case RETRACTING:moveTongue(startTongue*(1-ease(float(e)/TONGUE_IN_MS)));if(e>=TONGUE_IN_MS)enter(CLOSING);break;
    case CLOSING:moveJaw(startJaw*(1-ease(float(e)/JAW_MS)));if(e>=JAW_MS){homed=true;enter(RESTING);}break;
    case RESTING:if(e>=350){if(--repeats>0)enter(OPENING);else enter(IDLE);}break;
  }
}
void manualPulse(bool isJaw,const char *value){
  if(armed||stage!=IDLE){Serial.println("DISARM first. Calibration is for disconnected drives only.");return;}
  char *end;long pulse=strtol(value,&end,10);
  if(end==value||*end||pulse<800||pulse>2350){Serial.println("Use JAW or TONGUE followed by 800..2350 microseconds.");return;}
  Servo &drive=isJaw?jaw:tongue;
  if(!attachDrive(drive,isJaw?JAW_PIN:TONGUE_PIN,pulse))return;
  if(isJaw)jawPos=float(pulse-JAW_CLOSED_US)/(JAW_OPEN_US-JAW_CLOSED_US);
  else tonguePos=float(pulse-TONGUE_IN_US)/(TONGUE_OUT_US-TONGUE_IN_US);
  homed=false;
  Serial.print("Calibration pulse: ");Serial.println(pulse);
}
void printHelp(){
  Serial.println("SET YYYY-MM-DD HH:MM:SS | HOME | ARM | DEMO | DISARM | STATUS");
  Serial.println("Unloaded calibration only: JAW <microseconds> | TONGUE <microseconds>");
}
void command(){
  if(!strcmp(line,"ARM")){
    if(!homed||stage!=IDLE)Serial.println("Run HOME and wait for it to finish first.");
    else{armed=true;Serial.println("Armed. DEMO runs one cuckoo; valid time enables hourly operation.");}
  }
  else if(!strcmp(line,"DISARM")){armed=false;homed=false;enter(IDLE);if(USE_BUZZER)noTone(BUZZER_PIN);Serial.println("Stopped; servos hold their last commands. HOME retracts then closes.");}
  else if(!strcmp(line,"HOME")){armed=false;homed=false;if(USE_BUZZER)noTone(BUZZER_PIN);if(attachBoth()){repeats=1;enter(RETRACTING);}}
  else if(!strcmp(line,"DEMO")){if(!armed||!homed||stage!=IDLE)Serial.println("Run HOME, wait, then ARM first; DEMO requires idle.");else beginCuckoo(1);}
  else if(!strncmp(line,"JAW ",4))manualPulse(true,line+4);
  else if(!strncmp(line,"TONGUE ",7))manualPulse(false,line+7);
  else if(!strncmp(line,"SET ",4)){
    unsigned y,mo,d,h,mi,s;
    bool format=strlen(line)==23;
    for(uint8_t i=4;format&&i<23;i++){
      char expected=i==8||i==11?'-':i==14?' ':i==17||i==20?':':0;
      format=expected?line[i]==expected:(line[i]>='0'&&line[i]<='9');
    }
    if(format && sscanf(line+4,"%4u-%2u-%2u %2u:%2u:%2u",&y,&mo,&d,&h,&mi,&s)==6 && y<=2099 && mo<=12 && d<=31 && h<=23 && mi<=59 && s<=59){
      Clock c={(uint16_t)y,(uint8_t)mo,(uint8_t)d,(uint8_t)h,(uint8_t)mi,(uint8_t)s};
      bool ok=setClock(c);rtcGood=readClock();
      Serial.println(ok?"RTC set to local time.":"Invalid date or RTC error.");
    }else Serial.println("Use SET YYYY-MM-DD HH:MM:SS");
  }else if(!strcmp(line,"STATUS")){
    rtcGood=readClock();Serial.print("RTC=");Serial.print(rtcGood);Serial.print(" armed=");Serial.print(armed);
    Serial.print(" homed=");Serial.print(homed);Serial.print(" stage=");Serial.println(int(stage));
    if(rtcGood){char stamp[24];snprintf(stamp,sizeof(stamp),"%04u-%02u-%02u %02u:%02u:%02u",now.year,now.month,now.day,now.hour,now.minute,now.second);Serial.println(stamp);}
  }else printHelp();
}
void setup(){
  Serial.begin(115200);
  if(USE_DS3231)Wire.begin();else RTC.begin();
  if(USE_DISPLAY){pinMode(CLK_PIN,OUTPUT);digitalWrite(CLK_PIN,HIGH);dio(true);}
  // Default: no servo pulses until HOME or an explicit calibration command.
  pinMode(JAW_PIN,OUTPUT);digitalWrite(JAW_PIN,LOW);
  pinMode(TONGUE_PIN,OUTPUT);digitalWrite(TONGUE_PIN,LOW);
  if(USE_BUZZER){pinMode(BUZZER_PIN,OUTPUT);digitalWrite(BUZZER_PIN,LOW);}
  if(AUTO_ARM_AFTER_CALIBRATION&&attachBoth()){homed=true;armed=true;}
  rtcGood=readClock();displayClock();
  Serial.println("Piranha Clock V6 ready. Calibrate with drives disconnected. See ELECTRONICS.md.");
  printHelp();
}
void loop(){
  // Bound serial work so a continuous input stream cannot starve motion.
  for(uint8_t n=0;n<64&&Serial.available();n++){
    char c=Serial.read();
    if(c=='\n'||c=='\r'){
      if(lineOverflow)Serial.println("Command too long; ignored.");
      else if(used){line[used]=0;command();}
      used=0;lineOverflow=false;
    }else if(!lineOverflow){if(used<sizeof(line)-1)line[used++]=c;else lineOverflow=true;}
  }
  if(millis()-lastClockRead>=200){
    lastClockRead=millis();rtcGood=readClock();displayClock();
    if(rtcGood){uint32_t key=((((uint32_t)now.year*13+now.month)*32+now.day)*24+now.hour);
      if(now.minute==0 && now.second<3 && key!=lastHourKey){lastHourKey=key;if(now.hour>=QUIET_END&&now.hour<QUIET_START)beginCuckoo(now.hour%12?now.hour%12:12);}
    }
  }
  motion();
}
