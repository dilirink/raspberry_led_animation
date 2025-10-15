#!/usr/bin/env python
# НАЗВАНИЕ: Трансформация точек
# ОПИСАНИЕ: Морфинг белых точек между различными геометрическими паттернами
import random
import numpy as np
from  rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
# from  RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
import time

# Настройки матрицы


options = RGBMatrixOptions()
options.hardware_mapping = 'adafruit-hat'
options.rows = 64
options.cols = 64
options.brightness = 100



matrix = RGBMatrix(options=options)
offscreen_canvas = matrix.CreateFrameCanvas()

# Размеры матрицы
GRID_SIZE = 64

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Исходные фигуры (массивы из оригинального файла)
shapes_data =  [
      " ?!?\"?#?$?%?&?'?(?)?*?+?,?-?.?/?0?1?2?3?4?5?6?7?8?9?:?;?<?=?>???@?A?B?C?D?E?F?G?H?I?J?K?L?M?N?O?P?Q?R?S?T?U?V?W?X?Y?Z?[?\\?]?^?_?",
  "  \" $ & ( * , . 0 2 4 6 8 : < > @ B D F H J L N P R T V X Z \\ ^ !_#_%_'_)_+_-_/_1_3_5_7_9_;_=_?_A_C_E_G_I_K_M_O_Q_S_U_W_Y_[_]___",
  "?0?1?2?3?4?5?6?7?8?9?:?;?<?=?>??@?A?B?C?D?E?F?G?H?I?J?K?L?M?N?O?0@1@2@3@4@5@6@7@8@9@:@;@<@=@>@?@@@@A@B@C@D@E@F@G@H@I@J@K@L@M@N@O",
  '?!?"?%?&?)?*?-?.?1?2?5?6?9?:?=?>A?B?E?F?I?J?M?N?Q?R?U?V?Y?Z?]?^?!@"@%@&@)@*@-@.@1@2@5@6@9@:@=@>@@A@B@E@F@I@J@M@N@Q@R@U@V@Y@Z@]@^',
  "<<=<><?<@<A<B<C<<===>=?=@=A=B=C=<>=>>>?>@>A>B>C><?=?>???@?A?B?C?<@=@>@?@@@A@B@C@<A=A>A?A@AAABACA<B=B>B?B@BABBBCB<C=C>C?C@CACBCCC",
  "../.0.1.N.O.P.Q..///0/1/N/O/P/Q/.0/00010N0O0P0Q0.1/10111N1O1P1Q1.N/N0N1NNNONPNQN.O/O0O1ONOOOPOQO.P/P0P1PNPOPPPQP.Q/Q0Q1QNQOQPQQQ",
  ">1?1@1A1>2A2>3A3>4A4>5A5>6A6>7A7>8A8>9A9>:A:>;A;><A<>=A=>>A>>?A?>@A@>AAA>BAB>CAC>DAD>EAE>FAF>GAG>HAH>IAI>JAJ>KAK>LAL>MAM>N?N@NAN",
  "=2>2?2@2A2B2=3B3=4B4=5B5=6B6=7B7=8B8=9B9=:B:=;B;=<B<==B==>B>=?B?=@B@=ABA=BBB=CBC=DBD=EBE=FBF=GBG=HBH=IBI=JBJ=KBK=LBL=M>M?M@MAMBM",
  ";4<4=4>4?4@4A4B4C4D4;5D5;6D6;7D7;8D8;9D9;:D:;;D;;<D<;=D=;>D>;?D?;@D@;ADA;BDB;CDC;DDD;EDE;FDF;GDG;HDH;IDI;JDJ;K<K=K>K?K@KAKBKCKDK",
  ":5;5<5=5>5?5@5A5B5C5D5E5:6E6:7E7:8E8:9E9::E::;E;:<E<:=E=:>E>:?E?:@E@:AEA:BEB:CEC:DED:EEE:FEF:GEG:HEH:IEI:J;J<J=J>J?J@JAJBJCJDJEJ",
  "96:6;6<6=6>6?6@6A6B6C6D6E6F697F798F899F99:F:9;F;9<F<9=F=9>F>9?F?9@F@9AFA9BFB9CFC9DFD9EFE9FFF9GFG9HFH9I:I;I<I=I>I?I@IAIBICIDIEIFI",
  "8797:7;7<7=7>7?7@7A7B7C7D7E7F7G788G889G98:G:8;G;8<G<8=G=8>G>8?G?8@G@8AGA8BGB8CGC8DGD8EGE8FGF8GGG8H9H:H;H<H=H>H?H@HAHBHCHDHEHFHGH",
  "  0 O _ $$4$K$[$((8(G(W(,,<,C,S, 000O0_0$444K4[4(888G8W8,<<<C<S<,C<CCCSC(G8GGGWG$K4KKK[K O0OOO_O,S<SCSSS(W8WGWWW$[4[K[[[ _0_O___",
  "//P/00O011N122M233L344K455J566I677H788G899F9::E:;;D;<<C<==B=>>A>>AAA=BBB<CCC;DDD:EEE9FFF8GGG7HHH6III5JJJ4KKK3LLL2MMM1NNN0OOO/PPP",
  "  _ !!^!\"\"]\"##\\#$$[$%%Z%&&Y&''X'((W())V)**U*++T+,,S,--R-..Q.//P//PPP.QQQ-RRR,SSS+TTT*UUU)VVV(WWW'XXX&YYY%ZZZ$[[[#\\\\\\\"]]]!^^^ ___",
  "/000O0P0.111N1Q1-222M2R2,333L3S3+444K4T4*555J5U5)666I6V6(777H7W7'888G8X8&999F9Y9%:::E:Z:$;;;D;[;#<<<C<\\<\"===B=]=!>>>A>^> ???@?_?",
  "0/1/2/3/4/5/6/7/8/9/:/;/</=/>/?/@/A/B/C/D/E/F/G/H/I/J/K/L/M/N/O//0P0.1Q1-2R2,3S3+4T4*5U5)6V6(7W7'8X8&9Y9%:Z:$;[;#<\\<\"=]=!>^> ?_?",
  "0 /!1!.\"2\"-#3#,$4$+%5%*&6&)'7'((8(')9)&*:*%+;+$,<,#-=-\".>.!/?/ 0!0\"0#0$0%0&0'0(0)0*0+0,0-0.0/000102030405060708090:0;0<0=0>0?0@0",
  "  ! \" # $ % & ' ( ) * + , - . / 0 1 2 3 4 5  !5! \"4\" #3# $2$ %1% &0& '/' (.( )-) *,* +++ ,*, -)- .(. /'/ 0&0 1%1 2$2 3#3 4\"4 5!5",
  "  _ =*B*8.=.B.G.3383=3B3G3L3.83888=8B8G8L8Q8)=.=3=8===B=G=L=Q=V=)B.B3B8B=BBBGBLBQBVB.G3G8G=GBGGGLGQG3L8L=LBLGLLL8Q=QBQGQ=VBV ___",
  '  " $ & V Y \\ _  """$"&"V#Y#\\#_# $"$$$&$ &"&$&&&V&Y&\\&_&V)Y)\\)_) D)D2D;D M)M2M;MPPUPZP_PPUUUZU_U V)V2V;VPZUZZZ_Z _)_2_;_P_U_Z___',
  '  " $ & ( * , . "!$!&!(!*!,!.!""$"&"("*","."$#&#(#*#,#.#$$&$($*$,$.$&%(%*%,%.%&&(&*&,&.&(\'*\',\'.\'((*(,(.(*),).)**,*.*,+.+,,.,.-..',
  "  & ' . / 6 7 > ? F G N O V W ^ _  !_&_' ( )_._/ 0 1_6_7 8 9_>_? @ A_F_G H I_N_O P Q_V_W X Y_^ _!_(_)_0_1_8_9_@_A_H_I_P_Q_X_Y___",
  "OOPOQOROSOTOUOVOWOXOYOZO[O\\O]O^O_OOP_POQ_QOR_ROS_SOT_TOU_UOV_VOW_WOX_XOY_YOZ_ZO[_[O\\_\\O]_]O^_^O_P_Q_R_S_T_U_V_W_X_Y_Z_[_\\_]_^___",
  "0?/@1@.A2A-B3B,C4C+D5D*E6E)F7F(G8G'H9H&I:I%J;J$K<K#L=L\"M>M!N?N O@O!P?P\"Q>Q#R=R$S<S%T;T&U:U'V9V(W8W)X7X*Y6Y+Z5Z,[4[-\\3\\.]2]/^1^0_",
  "? A!=\"C#;$E%9&G'7(I)5*K+3,M-1.O//0Q1-2S3+4U5)6W7'8Y9%:[;#<]=!>_? @^A\"B\\C$DZE&FXG(HVI*JTK,LRM.NPO0PNQ2RLS4TJU6VHW8XFY:ZD[<\\B]>^@_",
  "_ ^!]\"\\#[$Z%Y&X'W(V)U*T+S,R-Q.P/O0N1M2L3K4J5I6H7G8F9E:D;C<B=A>@??@>A=B<C;D:E9F8G7H6I5J4K3L2M1N0O/P.Q-R,S+T*U)V(W'X&Y%Z$[#\\\"]!^ _",
  "!?#?%?'?)?+?-?/?1?3?5?7?9?;?=???A?C?E?G?I?K?M?O?Q?S?U?W?Y?[?]?_? @\"@$@&@(@*@,@.@0@2@4@6@8@:@<@>@@@B@D@F@H@J@L@N@P@R@T@V@X@Z@\\@^@",
  "@ A!B\"C#D$E%F&G'H(I)J*K+L,M-N.O/P0Q1R2S3T4U5V6W7X8Y9Z:[;\\<]=^>_??@>A=B<C;D:E9F8G7H6I5J4K3L2M1N0O/P.Q-R,S+T*U)V(W'X&Y%Z$[#\\\"]!^ _",
  "@ @!@\"@#@$@%@&@'@(@)@*@+@,@-@.@/@0@1@2@3@4@5@6@7@8@9@:@;@<@=@>@??@>A=B<C;D:E9F8G7H6I5J4K3L2M1N0O/P.Q-R,S+T*U)V(W'X&Y%Z$[#\\\"]!^ _",
  "?@@@>AAA=BBB<CCC;DDD:EEE9FFF8GGG7HHH6III5JJJ4KKK3LLL2MMM1NNN0OOO/PPP.QQQ-RRR,SSS+TTT*UUU)VVV(WWW'XXX&YYY%ZZZ$[[[#\\\\\\\"]]]!^^^ ___",
  "?@@@A@B@C@D@E@F@G@H@I@J@K@L@M@N@O@P@Q@R@S@T@U@V@W@X@Y@Z@[@\\@]@^@_@>A=B<C;D:E9F8G7H6I5J4K3L2M1N0O/P.Q-R,S+T*U)V(W'X&Y%Z$[#\\\"]!^ _",
  "0?1?2?3?4?5?6?7?8?9?:?;?<?=?>???@?A?B?C?D?E?F?G?H?I?J?K?L?M?N?O?0@1@2@3@4@5@6@7@8@9@:@;@<@=@>@?@@@A@B@C@D@E@F@G@H@I@J@K@L@M@N@O@",
  "(&H&('6'7'8'9'H'V'W'X'Y'((H(()H)76W677W7&8'8(8)878F8G8H8I8W879W9(FHF(G6G7G8G9GHGVGWGXGYG(HHH(IHI7VWV7WWW&X'X(X)X7XFXGXHXIXWX7YWY",
  "99:9=9>9A9B9E9F99:::=:>:A:B:E:F:9=:===>=A=B=E=F=9>:>=>>>A>B>E>F>9A:A=A>AAABAEAFA9B:B=B>BABBBEBFB9E:E=E>EAEBEEEFE9F:F=F>FAFBFEFFF",
  "3343;3<3C3D3K3L33444;4<4C4D4K4L43;4;;;<;C;D;K;L;3<4<;<<<C<D<K<L<3C4C;C<CCCDCKCLC3D4D;D<DCDDDKDLD3K4K;K<KCKDKKKLK3L4L;L<LCLDLKLLL",
  "''('7'8'G'H'W'X''(((7(8(G(H(W(X('7(77787G7H7W7X7'8(87888G8H8W8X8'G(G7G8GGGHGWGXG'H(H7H8HGHHHWHXH'W(W7W8WGWHWWWXW'X(X7X8XGXHXWXXX",
  "'Q&R(R%S'S)S$T&T(T*T#U%U'U)U+U\"V$V&V(V*V,V!W#W%W'W)W+W-W X\"X$X&X(X*X,X.X!Y#Y%Y'Y)Y+Y-Y\"Z$Z&Z(Z*Z,Z#[%['[)[+[$\\&\\(\\*\\%]'])]&^(^'_",
  "'C&E(E%G'G)G$I&I(I*I#K%K'K)K+K\"M$M&M(M*M,M!O#O%O'O)O+O-O Q\"Q$Q&Q(Q*Q,Q.Q!S#S%S'S)S+S-S\"U$U&U(U*U,U#W%W'W)W+W$Y&Y(Y*Y%['[)[&](]'_",
  '.C,E0E*G.G2G(I,I0I4I&K*K.K2K6K$M(M,M0M4M8M"O&O*O.O2O6O:O Q$Q(Q,Q0Q4Q8Q<Q"S&S*S.S2S6S:S$U(U,U0U4U8U&W*W.W2W6W(Y,Y0Y4Y*[.[2[,]0]._',
  "  ! \\ ] ^ _  !!!\\!_!\\\"_\"\\#]#^#_# X!X\"X#X$X%X&X'X Y'Y Z'ZZZ[Z\\Z]Z^Z_Z ['[Z[_[ \\'\\Z\\_\\ ]']Z]_] ^'^Z^_^ _!_\"_#_$_%_&_'_Z_[_\\_]_^___",
  "  ) 2 ; D M V _  )))2);)D)M)V)_) 2)222;2D2M2V2_2 ;);2;;;D;M;V;_; D)D2D;DDDMDVD_D M)M2M;MDMMMVM_M V)V2V;VDVMVVV_V _)_2_;_D_M_V___",
  "  \" $ & ( * , . 0 2 4 6 8 : < > @ B D F H J L N P R T V X Z \\ ^ _!_#_%_'_)_+_-_/_1_3_5_7_9_;_=_?_A_C_E_G_I_K_M_O_Q_S_U_W_Y_[_]__",
  '  " % ) . 4 ; C  """%")"."4";"C" %"%%%)%.%4%;%C% )")%))).)4);)C) .".%.)...4.;.C. 4"4%4)4.444;4C4 ;";%;);.;4;;;C; C"C%C)C.C4C;CCC',
  '  * 4 >  !*! "*"4">" #*# $*$4$>$ %*% &*&4&>& \'*\' (*(4(>( )*) ***4*>* +*+ ,*,4,>, -*- .*.4.>. /*/ 0*040>0 1*1 2*242>2 3*3 4*444>4',
  '  3 F  ! "3" # $3$ % &3& \' (3(F( ) *3* + ,3, - .3. / 030 1 232F2 3 434 5 636 7 838 9 :3: ; <3<F< = >3> ? @3@ A B3B C D3D E F3FFF',
  "0(0)0*0+0,0-0.0/00H0I0J0K0L0M0N0O0P0Q0R0S0T0U0V0W001020304050607OHOIOJOKOLOMON(O)O*O+O,O-O.O/O0O1O2O3O4O5O6O7OOOOPOQOROSOTOUOVOW",
  "00@011A122B233C344D455E566F677G788H899I9::J:;;K;<<L<==M=>>N>??O??@O@>ANA=BMB<CLC;DKD:EJE9FIF8GHG7HGH6IFI5JEJ4KDK3LCL2MBM1NAN0O@O",
  "  ! \" # $ % & '  !'! \"'\" #'# $'$ %'% &'& '!'\"'#'$'%'&'''ZZ[Z\\Z]Z^Z_ZZ[[[\\[][^[_[Z\\[\\\\\\]\\^\\_\\Z][]\\]]]^]_]Z^[^\\^]^^^_^Z_[_\\_]_^___",
  "?7@7?8@8?9@9?:@:?;@;?<@<?=@=?>@>7?8?9?:?;?<?=?>?A?B?C?D?E?F?G?H?7@8@9@:@;@<@=@>@A@B@C@D@E@F@G@H@?A@A?B@B?C@C?D@D?E@E?F@F?G@G?H@H",
  '  ! " # $ % & \' ( ) *  !*! """#"$"%"&"\'"("*" #"#(#*# $"$($*$ %"%(%*% &"&(&*& \'"\'(\'*\' ("(#($(%(&(\'(((*( )*) *!*"*#*$*%*&*\'*(*)***',
  '  ! " $ % & ( ) * , - . 0 1 2 4 5 6 8 9 : < = >  !"!$!&!(!*!,!.!0!2!4!6!8!:!<!>! "!"""$"%"&"(")"*","-"."0"1"2"4"5"6"8"9":"<"=">"',
  '%"*"E"J""%-%B%M%"*-*B*M*%-*-E-J-52:2U2Z225=5R5]52:=:R:]:5=:=U=Z=%B*BEBJB"E-EBEME"J-JBJMJ%M*MEMJM5Q:QUQZQ2T=TRT]T2Y=YRY]Y5\\:\\U\\Z\\',
  "2090=0D0K0O00242B2F22494=4D4K4O40949;9B9F9M99;=;K;O;0=4=;=B=F=M=2B9B=BDBKBOB0D4DBDFD2F9F=FDFKFOF0K4K;KBKFKMK9M=MKMOM0O4O;OBOFOMO",
  "(0)0*0+0,0-0.0/00010203040506070H0I0J0K0L0M0N0O0P0Q0R0S0T0U0V0W00HOH0IOI0JOJ0KOK0LOL0MOM0NON0OOO0POP0QOQ0ROR0SOS0TOT0UOU0VOV0WOW",
  ">/A/:0E072H244=4B4K496F627M7>8A869I90:::E:O:><A<4=K=/>8><>C>G>P>/A8A<ACAGAPA4BKB>CAC0E:EEEOE6FIF>GAG2HMH9IFI4K=KBKKK7MHM:OEO>PAP",
  '@ A B C D E F H I J K L P Q R X @!A!B!C!D!E!F!H!I!J!K!L!P!Q!R!X!@"A"B"C"D"E"F"H"I"J"K"L"P"Q"R"X"@#A#B#C#D#E#F#H#I#J#K#L#P#Q#R#X#',
  "0(0)0*0+0,0-0.0/00H0I0J0K0L0M0N0O0P0Q0R0S0T0U0V0W0010203040506070HOH0IOI0JOJ0KOK0LOL0MOM0NON0OOO0POP0QOQ0ROR0SOS0TOT0UOU0VOV0WOW",
  "  !!\"\"##$$%%&&''(())**++,,--..//00112233445566778899::_;_<_=_>_?_@_A_B_C_D_E_F_G_H_I_J_K_L_M_N_O_P_Q_R_S_T_U_V_W_X_Y_Z_[_\\_]_^__",
  "( '!)!&\"*\"%#+#$$,$#%-%\"&.&!'/' (0(!)/)\"*.*#+-+$,,,%-+-&.*.'/)/(0WWXWYWZW[W\\W]W^W_WWX_XWY_YWZ_ZW[_[W\\_\\W]_]W^_^W_X_Y_Z_[_\\_]_^___",
  "&&9&F&Y&''8'G'X'((7(H(W())6)I)V))666I6V6(777H7W7'888G8X8&999F9Y9&F9FFFYF'G8GGGXG(H7HHHWH)I6IIIVI)V6VIVVV(W7WHWWW'X8XGXXX&Y9YFYYY",
  ' C$C(C,C0C4C8C<C"E&E*E.E2E6E:E$G(G,G0G4G8G<G&I*I.I2I6I:I(K,K0K4K8K<K*M.M2M6M:M,O0O4O8O<O.Q2Q6Q:Q0S4S8S<S2U6U:U4W8W<W6Y:Y8[<[:]<_',
  '  " $ & ( * , . !!#!%!\'!)!+!-! """$"&"("*","!###%#\'#)#+# $"$$$&$($*$!%#%%%\'%)% &"&$&&&(&!\'#\'%\'\'\' ("($(&(!)#)%) *"*$*!+#+ ,",!- .',
  "QQRRQSSSRTTTQUSUUURVTVVVQWSWUWWWRXTXVXXXQYSYUYWYYYRZTZVZXZZZQ[S[U[W[Y[[[R\\T\\V\\X\\Z\\\\\\Q]S]U]W]Y][]]]R^T^V^X^Z^\\^^^Q_S_U_W_Y_[_]___",

]
def convert_shape(shape_str):
    """Нормализация координат в диапазон 0-63"""
    nums = [(ord(ch) - 32) % GRID_SIZE for ch in shape_str]
    return [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]

shapes = [convert_shape(s) for s in shapes_data]
shape_order = list(range(len(shapes)))
random.shuffle(shape_order)

current_index = 0
current_points = np.array(shapes[shape_order[current_index]], dtype=float)
target_points = np.array(shapes[shape_order[current_index]], dtype=int)
transition_speed = 1

is_waiting = False
waiting_start = 0

try:
    while True:
        # Очистка буфера
        offscreen_canvas.Fill(*BLACK)

        # Логика анимации
        if not is_waiting:
            diffs = target_points - current_points
            steps = np.sign(diffs) * np.minimum(np.abs(diffs), transition_speed)
            current_points += steps

            if np.all(current_points == target_points):
                waiting_start = time.time()
                is_waiting = True
        else:
            if time.time() - waiting_start >= 2:
                current_index = (current_index + 1) % len(shapes)
                target_points = np.array(shapes[shape_order[current_index]], dtype=int)
                is_waiting = False

        # Отрисовка в буфер
        for x, y in current_points.astype(int):
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                offscreen_canvas.SetPixel(x, y, *WHITE)

        # Отправка буфера на матрицу
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        time.sleep(1/40)

except KeyboardInterrupt:
    matrix.Clear()