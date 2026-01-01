# Data Quality Report

- 생성시간 : `20260101`
- 대상 데이터 셋 : (mysql) novels(100483), novel_sources(129294), job_runs
-                (mongodb) novel_meta(100601)

## 이상치 통계
|   author_outlier_ratio |   genre_outlier_ratio |   mongo_outlier_ratio |   episode_outlier_ratio |   view_outlier_ratio |   description_outlier_ratio |
|-----------------------:|----------------------:|----------------------:|------------------------:|---------------------:|----------------------------:|
|                      0 |                     0 |                     0 |                       0 |                    0 |                           0 |

## 결측치 검사
|   total |   failed |   skipped |   success |   duration_ms | platform_slug   |
|--------:|---------:|----------:|----------:|--------------:|:----------------|
|   57042 |        0 |      1208 |     55834 |      99683055 | KP              |
|  100386 |        2 |     27208 |     73176 |      10701573 | NS              |

## 중복 비율
### description 중복
|   duplicate_numbers |   counts |
|--------------------:|---------:|
|                   2 |    16655 |
|                   3 |     1564 |
|                   4 |      107 |
|                   5 |       17 |
|                   6 |        8 |
|                   7 |        2 |
|                   8 |        2 |

### 같은 플랫폼 중복 소설
|    |   cnt |   novel_id | slug   |
|---:|------:|-----------:|:-------|
|  0 |     2 |        619 | KP     |
|  1 |     2 |       6201 | KP     |
|  2 |     2 |       7024 | KP     |
|  3 |     2 |       8710 | KP     |
|  4 |     2 |       9379 | KP     |
|  5 |     2 |      12216 | KP     |
|  6 |     2 |      18951 | KP     |
|  7 |     2 |      29382 | KP     |
|  8 |     2 |      43637 | KP     |
|  9 |     2 |      52032 | KP     |
| 10 |     2 |      58616 | KP     |
| 11 |     2 |      63945 | KP     |
| 12 |     2 |      65954 | KP     |
| 13 |     2 |      72375 | KP     |
| 14 |     2 |      74586 | KP     |
| 15 |     2 |      74758 | KP     |
| 16 |     2 |      75102 | KP     |
| 17 |     2 |      75221 | KP     |
| 18 |     2 |      76575 | KP     |
| 19 |     2 |      77064 | KP     |
| 20 |     2 |      79028 | KP     |
| 21 |     2 |      79687 | KP     |
| 22 |     2 |      81472 | KP     |
| 23 |     2 |      82659 | KP     |
| 24 |     2 |      82765 | KP     |
| 25 |     2 |      93755 | KP     |
| 26 |     2 |     112944 | KP     |
| 27 |     2 |     116602 | KP     |
| 28 |     2 |     117753 | KP     |
| 29 |     2 |     121372 | KP     |
| 30 |     2 |     121969 | KP     |
| 31 |     2 |     122480 | KP     |
| 32 |     2 |     124789 | KP     |
| 33 |     2 |     125481 | KP     |
| 34 |     2 |     127632 | KP     |
| 35 |     2 |     130039 | KP     |
| 36 |     2 |     138628 | KP     |
| 37 |     2 |     140765 | KP     |
| 38 |     2 |     146099 | KP     |
| 39 |     2 |     152290 | KP     |
| 40 |     2 |     155818 | KP     |
| 41 |     2 |     156920 | KP     |
| 42 |     2 |     158605 | KP     |
| 43 |     2 |     170311 | KP     |
| 44 |     2 |     170315 | KP     |
| 45 |     2 |     172957 | KP     |
| 46 |     2 |     179600 | KP     |
| 47 |     2 |       2581 | NS     |
| 48 |     2 |       3459 | NS     |
| 49 |     2 |       3768 | NS     |
| 50 |     2 |       4187 | NS     |
| 51 |     2 |       4376 | NS     |
| 52 |     2 |       9596 | NS     |
| 53 |     2 |       9811 | NS     |
| 54 |     2 |      14991 | NS     |
| 55 |     2 |      18857 | NS     |
| 56 |     2 |      21135 | NS     |
| 57 |     2 |      21207 | NS     |
| 58 |     2 |      22249 | NS     |
| 59 |     2 |      24786 | NS     |
| 60 |     2 |      27346 | NS     |
| 61 |     2 |      27817 | NS     |
| 62 |     2 |      30281 | NS     |
| 63 |     2 |      31139 | NS     |
| 64 |     2 |      32253 | NS     |
| 65 |     2 |      33692 | NS     |
| 66 |     2 |      37174 | NS     |
| 67 |     2 |      39069 | NS     |
| 68 |     2 |      41237 | NS     |
| 69 |     2 |      42692 | NS     |
| 70 |     2 |      42730 | NS     |
| 71 |     2 |      43187 | NS     |
| 72 |     2 |      48325 | NS     |
| 73 |     2 |      49042 | NS     |
| 74 |     2 |      49780 | NS     |
| 75 |     2 |      51568 | NS     |
| 76 |     2 |      53552 | NS     |
| 77 |     2 |      55982 | NS     |
| 78 |     2 |      57124 | NS     |
| 79 |     2 |      57188 | NS     |
| 80 |     2 |      58754 | NS     |

## Rule 위반 (매핑 안 된 것들)
### MySQL만 존재
| MySQL_author   | MySQL_title   | mongo_doc_id   | Mongo_title   | Mongo_author   | _merge   |
|----------------|---------------|----------------|---------------|----------------|----------|

### MongoDB만 존재
|     |   MySQL_author |   MySQL_title | mongo_doc_id             | Mongo_title                 | Mongo_author   | _merge     |
|----:|---------------:|--------------:|:-------------------------|:----------------------------|:---------------|:-----------|
|   0 |            nan |           nan | 6935c4a154537270b357bd3b | 완벽한 후견인을 소유하는 일             | 탁상지            | right_only |
|   1 |            nan |           nan | 6935c4ae54537270b357bd83 | 사천당가 침술명의가 되었다              | 주문향            | right_only |
|   2 |            nan |           nan | 6935c4d754537270b357c00f | 대공 전하의 하나뿐인 손녀딸입니다          | 김크레파스          | right_only |
|   3 |            nan |           nan | 6935c54054537270b357c610 | 판테르논 황제의 남다른 취향 [단행본]       | Miss리베라        | right_only |
|   4 |            nan |           nan | 6935c56854537270b357c860 | 전생자는 무결점 재능천재               | 쏭범             | right_only |
|   5 |            nan |           nan | 6935c64054537270b357d495 | 몬스터는 몬스터로 막는다 [단행본]         | 의현Su           | right_only |
|   6 |            nan |           nan | 6935c6b854537270b357db5d | 이세계 갓물주로 살아가는 법             | fictionist     | right_only |
|   7 |            nan |           nan | 6935c71854537270b357e0ca | 우연 No!! 인연 Yes!!            | 투이아비           | right_only |
|   8 |            nan |           nan | 6935c72a54537270b357e1d2 | The 설렘                      | 이희정            | right_only |
|   9 |            nan |           nan | 6935c7b454537270b357e9b1 | 더러워서 내가 키운다 [단행본]           | 영화보는곰          | right_only |
|  10 |            nan |           nan | 6935c7c554537270b357eaa9 | 이세계 갓물주로 살아가는 법 [단행본]       | fictionist     | right_only |
|  11 |            nan |           nan | 6935c7d754537270b357eba3 | 인터넷으로 사회를 지배하는 방법[단행본]      | 블렝             | right_only |
|  12 |            nan |           nan | 6935c7f454537270b357ed4a | 3회차 전생 무신이 꿀빠는 법 [단행본]      | 세인토            | right_only |
|  13 |            nan |           nan | 6935c80c54537270b357eea6 | 발칙한 밤의 거짓말                  | 릴리s            | right_only |
|  14 |            nan |           nan | 6935c81f54537270b357efb2 | 남주를 죽여버렸다                   | 이이리            | right_only |
|  15 |            nan |           nan | 6935c83f54537270b357f17e | 천재 드루이드가 용을 먹었다             | 안밀             | right_only |
|  16 |            nan |           nan | 6935c85f54537270b357f362 | 크림슨 티어즈 [단행본]               | calendula      | right_only |
|  17 |            nan |           nan | 6935ca2a54537270b3580ce1 | 부적절한 계약                     | 김수정C           | right_only |
|  18 |            nan |           nan | 6935ca4454537270b3580e67 | 무림에서 무신이 된 썰 품              | 위진호            | right_only |
|  19 |            nan |           nan | 6935ca8c54537270b358126b | 운빨X망겜, 재능으로 압도한다!           | 추월             | right_only |
|  20 |            nan |           nan | 6935ca8f54537270b358129b | 그 용병이 게임에서 살아남는 법           | yongh          | right_only |
|  21 |            nan |           nan | 6935cb0554537270b3581931 | 인생 리셋 오 일병!                 | 세상s            | right_only |
|  22 |            nan |           nan | 6935cb8054537270b3582015 | 첫사랑 그놈은 오늘도 연체 중!           | 안교찬            | right_only |
|  23 |            nan |           nan | 6935cbaa54537270b358225f | 초능력무신                       | 운천룡            | right_only |
|  24 |            nan |           nan | 6935cbe354537270b3582583 | 돌체(dolce)                   | 서향             | right_only |
|  25 |            nan |           nan | 6935cc9954537270b3582fd4 | 오만과 열정 [개정증보판]              | 채도(한승주)        | right_only |
|  26 |            nan |           nan | 6935ccef54537270b3583494 | 먹방으로 성공하는 ‘전’ 공작부인          | S모씨            | right_only |
|  27 |            nan |           nan | 6935cd2054537270b358373d | 이 결혼의 계략을 나만 몰라             | 다이앤            | right_only |
|  28 |            nan |           nan | 6935cd2f54537270b3583816 | 천 원짜리 재벌                    | 구름맛양갱          | right_only |
|  29 |            nan |           nan | 6935cd3754537270b3583892 | 황제의 여우                      | 연(蓮)           | right_only |
|  30 |            nan |           nan | 6935ce2154537270b35845a6 | 띠아모 (Ti amo)                | 완전천재           | right_only |
|  31 |            nan |           nan | 6935ce9154537270b3584be1 | 혈마재림                        | Takeoff        | right_only |
|  32 |            nan |           nan | 6935ceb154537270b3584d65 | 딸기, 좋아하세요?                  | 흑설탕케이크         | right_only |
|  33 |            nan |           nan | 6935ceec54537270b358500f | 날 죽일 집착광공에게서 살아남는 법         | Miny           | right_only |
|  34 |            nan |           nan | 6935cf3554537270b358541a | 버프로 최강의 야구 선수               | YT0709         | right_only |
|  35 |            nan |           nan | 6935cf5754537270b3585600 | wind and grass              | 견마지로           | right_only |
|  36 |            nan |           nan | 6935cf8354537270b3585864 | 공주님 저주를 내려주세요               | S모씨            | right_only |
|  37 |            nan |           nan | 6935d00a54537270b3585ff9 | 미친 네크로맨서의 회귀 [단행본]          | Takeoff        | right_only |
|  38 |            nan |           nan | 6935d0a754537270b358689c | 월연가(月戀歌), 달을 그리는 노래         | 윤재인            | right_only |
|  39 |            nan |           nan | 6935d12454537270b3586f58 | 바이트 (Bite)                  | 김태영            | right_only |
|  40 |            nan |           nan | 6935d1a054537270b3587629 | 나 혼자만 편의점이 Level Up! [단행본]  | coldpig        | right_only |
|  41 |            nan |           nan | 6935d1c654537270b3587838 | 아카데미의 전쟁영웅이 되었다             | FACTO          | right_only |
|  42 |            nan |           nan | 6935d26054537270b35880af | 괜찮아요 [단행본]                  | 드리머.K          | right_only |
|  43 |            nan |           nan | 6935d2b854537270b3588572 | 폐품무학관 [단행본]                 | 들마루            | right_only |
|  44 |            nan |           nan | 6935d2ff54537270b3588963 | 달아나지 않도록 더 세게               | 도토리            | right_only |
|  45 |            nan |           nan | 6935d30c54537270b3588a24 | 마피아로 조선 독립                  | Lunstellar     | right_only |
|  46 |            nan |           nan | 6935d3de54537270b35895b2 | 고인물 게임 속 직업으로 각성하다          | primus         | right_only |
|  47 |            nan |           nan | 6935d48d54537270b3589f24 | 슬러거 프로젝트                    | 세야Rune         | right_only |
|  48 |            nan |           nan | 6935d4ad54537270b358a0e3 | 히어로 뺑소니 전담반 [단행본]           | gonnagetya     | right_only |
|  49 |            nan |           nan | 6935d4e854537270b358a419 | 최애작 주인공들의 딸이 되었는데 시한부라니요?   | 프리즘            | right_only |
|  50 |            nan |           nan | 6935d51554537270b358a688 | 천마가 되어 돌아온 막내황자             | 기아스            | right_only |
|  51 |            nan |           nan | 6935d56154537270b358aaa8 | 표정 읽는 재벌 형사                 | 탱솔             | right_only |
|  52 |            nan |           nan | 6935d56e54537270b358ab64 | 제육천주                        | 적하             | right_only |
|  53 |            nan |           nan | 6935d6d854537270b358beea | 데이트 메이트(Date mate)          | 서이나            | right_only |
|  54 |            nan |           nan | 6935d70c54537270b358c1b4 | 너를 사랑하기 위한 300일             | Snow           | right_only |
|  55 |            nan |           nan | 6935d74754537270b358c4e2 | 회귀하니 재능 99％ [단행본]           | 네모리노           | right_only |
|  56 |            nan |           nan | 6935d76754537270b358c69a | 가면을 만드는 마녀                  | 진올             | right_only |
|  57 |            nan |           nan | 6935d76b54537270b358c6ce | 별에서 온 내 비서                  | 별빛k            | right_only |
|  58 |            nan |           nan | 6935d77e54537270b358c7d0 | 나는 무공을 가지고 환생했다             | Heve           | right_only |
|  59 |            nan |           nan | 6935d7a154537270b358c9b8 | 조선 최고의 밥상                   | 한만수tm          | right_only |
|  60 |            nan |           nan | 6935d7c154537270b358cb69 | 발로 뛰는 작가님                   | yongh          | right_only |
|  61 |            nan |           nan | 6935d7d154537270b358cc4a | 미친 네크로맨서의 회귀                | Takeoff        | right_only |
|  62 |            nan |           nan | 6935d80b54537270b358cf4d | 애니멀 엔터테이너                   | 달콤한ice         | right_only |
|  63 |            nan |           nan | 6935d8c854537270b358d994 | 셀럽(celebrity) [단행본]         | 해엘             | right_only |
|  64 |            nan |           nan | 6935d92254537270b358de6a | 천마를 삼켰다 [단행본]               | stay           | right_only |
|  65 |            nan |           nan | 6935d98154537270b358e370 | 공주님은 과로사가 싫습니다 [단행본]        | 참새대리           | right_only |
|  66 |            nan |           nan | 6935da5c54537270b358ef2f | 계약 연애에 흑심을 품지 말아주세요         | 진유다예           | right_only |
|  67 |            nan |           nan | 6935da7f54537270b358f118 | 미친놈이 연기를 했을 때 [단행본]         | 정용(正龍)         | right_only |
|  68 |            nan |           nan | 6935db7854537270b358fe73 | 별에서 온 내 비서 [단행본]            | 별빛k            | right_only |
|  69 |            nan |           nan | 6935dbb554537270b35901b1 | 고아인데 마법천재                   | 찬동             | right_only |
|  70 |            nan |           nan | 6935dc2654537270b359079d | 고종의 그레이트 게임                 | 조동신            | right_only |
|  71 |            nan |           nan | 6935dc3954537270b35908a1 | 신의 능력을 얻었다                  | 의향도            | right_only |
|  72 |            nan |           nan | 6935dcae54537270b3590ee1 | 상태창은 중요한 문제일까               | Writingbot     | right_only |
|  73 |            nan |           nan | 6935dd4f54537270b359175c | 환생이 싫은 천재 피아니스트 [단행본]       | 나나니벌           | right_only |
|  74 |            nan |           nan | 6935dd9d54537270b3591b7a | 백수귀환                        | 불군(不群)         | right_only |
|  75 |            nan |           nan | 6935ddb154537270b3591c89 | 마왕전생 RED                    | 홍정훈            | right_only |
|  76 |            nan |           nan | 6935dea554537270b3592972 | 사랑 Two                      | 장혜경            | right_only |
|  77 |            nan |           nan | 6935df4c54537270b359321a | 그대에게 ZOOM                   | 이바하            | right_only |
|  78 |            nan |           nan | 6935df6454537270b3593362 | 검존, 헌터가 되다 [단행본]            | GORDON         | right_only |
|  79 |            nan |           nan | 6935df7054537270b359340a | 짐승 대공을 조련하는 남장 여주입니다 [단행본]  | 얼그레이M          | right_only |
|  80 |            nan |           nan | 6935dfda54537270b3593997 | 공작가의 미친놈                    | 유현S            | right_only |
|  81 |            nan |           nan | 6935dff754537270b3593b24 | 언니, 이 백화점은 내 거야             | 해코스            | right_only |
|  82 |            nan |           nan | 6935e07654537270b35941b6 | 대장장이는 네크로맨서가 되었다 [단행본]      | 투곰대디           | right_only |
|  83 |            nan |           nan | 6935e08054537270b359423d | 크림슨 티어즈                     | calendula      | right_only |
|  84 |            nan |           nan | 6935e13c54537270b3594c03 | 몬스터는 몬스터로 막는다               | 의현Su           | right_only |
|  85 |            nan |           nan | 6935e1fd54537270b359560a | 이세계의 능력을 흡수함 6권 [단행본]       | 연함             | right_only |
|  86 |            nan |           nan | 6935e21a54537270b3595796 | 불사자 : 회귀해서 죽는다 [단행본]        | Heve           | right_only |
|  87 |            nan |           nan | 6935e22b54537270b3595883 | 스페이스 in 무림 [단행본]            | 들마루            | right_only |
|  88 |            nan |           nan | 6935e24b54537270b3595a29 | Blue_Moon’s_Devil (푸른달의 악마) | rotate         | right_only |
|  89 |            nan |           nan | 6935e35354537270b35967f2 | 제독님과 해적 선장이 나를 귀찮게 한다       | MapleMoose     | right_only |
|  90 |            nan |           nan | 6935e3ea54537270b3596fca | 그때 분명 공작 부인은 죽었다            | 네코다메론          | right_only |
|  91 |            nan |           nan | 6935e3f454537270b359704d | 그림자 계약                      | 은호             | right_only |
|  92 |            nan |           nan | 6935e49254537270b3597867 | 어차피 사랑일 테니                  | Carbo(도효원)     | right_only |
|  93 |            nan |           nan | 6935e56d54537270b35983d4 | 섬마을 소년이 대충 찍은 영상이 美쳤다       | 천해시            | right_only |
|  94 |            nan |           nan | 6935e59954537270b359861b | 발칙한 밤의 거짓말 [단행본]            | 릴리s            | right_only |
|  95 |            nan |           nan | 6935e5e554537270b3598a0c | 돈 버는 재능이 넘쳐나는 영주님           | 오토마톤G          | right_only |
|  96 |            nan |           nan | 6935e74a54537270b3599b35 | 황후 폐하께서는 정상이 아니시옵니다 [단행본]   | Miss리베라        | right_only |
|  97 |            nan |           nan | 6935e81954537270b359a5c0 | 증기시대의 야수조련사                 | 돌무지            | right_only |
|  98 |            nan |           nan | 6935e83254537270b359a71e | 불행을 먹고 회귀한 악녀는 오늘도 무럭무럭 자란다 | 애플97           | right_only |
|  99 |            nan |           nan | 6935e86354537270b359a9a9 | 우리 사장님은 드래곤                 | 송제연            | right_only |
| 100 |            nan |           nan | 6935e8c254537270b359ae8d | 탑 스타(Top Star)              | 양(梁)           | right_only |
| 101 |            nan |           nan | 6935e99d54537270b359b9da | 공방의 인형술사                    | 첫트             | right_only |
| 102 |            nan |           nan | 6935ea3054537270b359c14a | 나는 무공을 가지고 환생했다 [단행본]       | Heve           | right_only |
| 103 |            nan |           nan | 6935ea5054537270b359c2da | 버프로 최강의 야구 선수 [단행본]         | YT0709         | right_only |
| 104 |            nan |           nan | 6935eb6254537270b359d0cd | 공작가의 미친놈 [단행본]              | 유현S            | right_only |
| 105 |            nan |           nan | 6935eb7c54537270b359d21d | 축구황제 어서오고                   | zorba          | right_only |
| 106 |            nan |           nan | 6935ebc654537270b359d5da | 마이 레이디(My lady)             | 두사람            | right_only |
| 107 |            nan |           nan | 6935ebda54537270b359d6e4 | 서머 브리즈(summer breeze)       | 이화             | right_only |
| 108 |            nan |           nan | 6935ec2554537270b359daab | 혈마재림 [단행본]                  | Takeoff        | right_only |
| 109 |            nan |           nan | 6935ec2554537270b359daad | 불사자 : 회귀해서 죽는다              | Heve           | right_only |
| 110 |            nan |           nan | 6935ec9454537270b359e057 | 1979 김부장이 독재를 계승 중입니다!      | 아아연하게          | right_only |
| 111 |            nan |           nan | 6935ed0754537270b359e637 | 괜찮아요                        | 드리머.K          | right_only |
| 112 |            nan |           nan | 6935ed2454537270b359e7af | 검존, 헌터가 되다                  | GORDON         | right_only |
| 113 |            nan |           nan | 6935ed4554537270b359e955 | 선생님, 파이어볼이 이상해요!            | A메리카노          | right_only |
| 114 |            nan |           nan | 6935edd154537270b359f06a | 도둑고양이                       | 연(蓮)           | right_only |
| 115 |            nan |           nan | 6935ee2354537270b359f470 | 이세계 편의점 힐링 맹주가 되었다          | 처령             | right_only |
| 116 |            nan |           nan | 6935ee3254537270b359f533 | 천마를 삼켰다                     | stay           | right_only |
| 117 |            nan |           nan | 6935ee5e54537270b359f777 | 판테르논 황제의 남다른 취향             | Miss리베라        | right_only |
