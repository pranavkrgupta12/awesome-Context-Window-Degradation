# Table 3: Token Budget Ablation (Score-Gap Adaptive-k Proxy vs Fixed-k Baselines)

| Retriever   | Comparison                                      |   Adaptive Proxy Tokens |   Fixed Tokens | Token Savings %   | Adaptive Proxy Full Cov %   | Fixed Full Cov %   |   Coverage Relative Ratio |
|:------------|:------------------------------------------------|------------------------:|---------------:|:------------------|:----------------------------|:-------------------|--------------------------:|
| BM25        | Score-Gap Adaptive-k Proxy (k=2.22) vs Fixed-1  |                   263.2 |          101.8 | -158.6%           | 21.4%                       | 0.0%               |                     0     |
| BM25        | Score-Gap Adaptive-k Proxy (k=2.22) vs Fixed-3  |                   263.2 |          356.2 | 26.1%             | 21.4%                       | 45.6%              |                     0.469 |
| BM25        | Score-Gap Adaptive-k Proxy (k=2.22) vs Fixed-5  |                   263.2 |          616   | 57.3%             | 21.4%                       | 61.6%              |                     0.347 |
| BM25        | Score-Gap Adaptive-k Proxy (k=2.22) vs Fixed-10 |                   263.2 |         1226.8 | 78.5%             | 21.4%                       | 100.0%             |                     0.214 |
| TF-IDF      | Score-Gap Adaptive-k Proxy (k=2.02) vs Fixed-1  |                   200.6 |           84.9 | -136.4%           | 23.2%                       | 0.0%               |                     0     |
| TF-IDF      | Score-Gap Adaptive-k Proxy (k=2.02) vs Fixed-3  |                   200.6 |          297.9 | 32.7%             | 23.2%                       | 49.8%              |                     0.466 |
| TF-IDF      | Score-Gap Adaptive-k Proxy (k=2.02) vs Fixed-5  |                   200.6 |          538.7 | 62.8%             | 23.2%                       | 67.2%              |                     0.345 |
| TF-IDF      | Score-Gap Adaptive-k Proxy (k=2.02) vs Fixed-10 |                   200.6 |         1226.8 | 83.6%             | 23.2%                       | 100.0%             |                     0.232 |
