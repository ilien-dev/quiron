bands from 127 human texts, 43 held out

group                              n        judge_p_ai       judge_as_ai      score_median      score_14plus      ai_side_mean     overshot_mean  audit_fails_mean audit_clean_share
human-heldout                     43               0.0               0.0                21               1.0               0.6              1.12                 0               1.0
opus55                             9              0.78              0.78                18               1.0              3.11              0.22              0.22              0.78
sonnet55                           9               1.0               1.0                20               1.0              2.22                 0              0.22              0.78
fable52                            9              0.44              0.44                20               1.0              1.67              0.33              0.11              0.89
gpt61                              8               1.0               1.0              14.5              0.62              6.75                 0              1.38               0.0
terra                              8               1.0               1.0              16.0              0.88                 5                 0              1.12              0.25

AUC vs held-out humans                  opus55        sonnet55         fable52           gpt61           terra
sentence-length CV                       0.796           0.674           0.624           0.869           0.872
mean sentence length                     0.682           0.792           0.528           0.783            0.59
long words (7+) /1k                       0.53           0.695           0.437           0.997           0.959
mean word length                         0.581           0.735           0.399           0.997           0.939
nominalizations /1k                      0.432           0.506            0.31           0.988           0.919
lexical diversity MATTR-50               0.911           0.987           0.876             1.0           0.977
first person /1k                         0.496           0.683            0.76            0.89            0.83
contractions /1k                         0.558           0.711           0.709           0.762           0.592
repeated openers /100                    0.627            0.64           0.696           0.804            0.65
connective openers %                     0.832           0.881           0.891           0.839           0.779
commas /1k                               0.881           0.744           0.773           0.869           0.814
lists of three /1k                       0.946           0.879           0.848           0.991           0.985
plain words /1k                          0.734           0.705           0.506           0.672           0.605
parentheses /1k                          0.724           0.858           0.891           0.988           0.987
headings /1k                             0.413            0.76           0.752           0.529           0.462

FAIL rate per check   human-heldout          opus55        sonnet55         fable52           gpt61           terra
B1                               0               0               0               0            0.38            0.38
C1                               0            0.22            0.22            0.11             1.0            0.62
T1                               0               0               0               0               0            0.12

TELL or FAIL rate    human-heldout          opus55        sonnet55         fable52           gpt61           terra
A14b                         0.023               0               0           0.111               0           0.125
A17                          0.023               0               0               0               0               0
A19                          0.047               0               0               0            0.25               0
A1b                          0.163               0           0.222           0.222           0.375           0.625
A20                           0.07               0               0               0           0.125            0.25
A2b                          0.186               0               0               0               0               0
A32                              0               0               0               0               0           0.125
A8                           0.093           0.111               0               0            0.25            0.25
B1                           0.349           0.222           0.111               0           0.875             1.0
B2                            0.07               0           0.333               0           0.125            0.25

checklist AUC                0.251           0.375           0.252           0.801           0.881
