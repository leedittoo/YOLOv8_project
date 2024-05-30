#include<Servo.h>
Servo ms1;
Servo ms2;
void setup(){
    Serial.begin(9600);
    ms1.attach(2);
    ms1.write(0);

    ms2.attach(4);
    ms2.write(10);
}
void loop(){
    if(Serial.available()>0){
        char u = Serial.read();
        if(u != '\n'){
            if(u == '1') {
              delay(500);
              ms1.write(100);
              ms2.write(100);
              delay(2000);
              ms1.write(0);
              ms2.write(10);
              delay(2000);
            }
            else if(u == '0') {
              ms1.write(0);
              ms2.write(10);
              delay(2000);
            }
            else {
              ms1.write(0);
              ms2.write(10);
              delay(2000);
            }
          }
    delay(1000);
    }
}