<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f5ff;
        }
        .poster {
            width: 841mm; /* A1 width */
            height: 594mm; /* A1 height */
            margin: 20px auto;
            background: white;
            border: 1px solid #ddd;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-template-rows: auto auto auto;
            grid-gap: 25px;
            padding: 30px;
            box-sizing: border-box;
        }
        .header {
            grid-column: 1 / span 4;
            background: #003087; /* Walmart blue */
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .abstract {
            grid-column: 1 / span 4;
            background: #f8f8f8;
            padding: 25px;
            border-radius: 10px;
            border-left: 10px solid #FFC220; /* Walmart yellow */
            font-size: 22px;
            line-height: 1.5;
        }
        .methods, .results, .model-selection, .conclusion {
            padding: 25px;
            background: white;
            border-radius: 10px;
            border: 1px solid #eee;
            font-size: 20px;
            line-height: 1.5;
        }
        .methods {
            grid-column: 1;
            grid-row: 3;
        }
        .results {
            grid-column: 2;
            grid-row: 3;
        }
        .model-selection {
            grid-column: 3;
            grid-row: 3;
        }
        .conclusion {
            grid-column: 4;
            grid-row: 3;
            background: #f8f8f8;
            border-left: 10px solid #003087;
        }
        h1 {
            margin: 0;
            font-size: 70px;
        }
        h2 {
            color: #003087;
            border-bottom: 4px solid #FFC220;
            padding-bottom: 10px;
            font-size: 36px;
            margin-top: 0;
        }
        h3 {
            font-size: 28px;
            color: #003087;
        }
        .chart {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            border: 2px dashed #ccc;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: #666;
        }
        .chart p {
            margin: 10px 0;
        }
        .metric {
            display: inline-block;
            background: #eef5ff;
            padding: 15px;
            margin: 10px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 22px;
        }
        .model-card {
            background: #f8f8f8;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 6px solid #003087;
        }
        .best-model {
            background: #e8f4ea;
            border-left: 6px solid #4CAF50;
        }
        .authors {
            font-size: 40px;
            margin-top: 20px;
        }
        .affiliation {
            font-style: italic;
            margin-top: 15px;
            font-size: 30px;
        }
        ul, ol {
            padding-left: 25px;
        }
        li {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="poster">
        <div class="header">
            <h1>TIME SERIES ANALYSIS ON WALMART WEEKLY SALES DATA</h1>
            <p class="authors"><strong>Mohamed Sillah Kanu</strong></p>
            <p class="affiliation">MS Research Project, The George Washington University, USA</p>
        </div>

        <div class="abstract">
            <h2>Abstract</h2>
            <p>This project focuses on time series forecasting of weekly sales data for 45 Walmart stores in the US, using the "Walmart_Cleaned_Data" dataset. The dataset satisfies criteria for time series analysis, being multivariate with 15 continuous numerical features. It contains 421,570 samples, is non-classified, and exhibits both seasonal patterns and overall trends. The data undergoes a thorough cleaning process, with no missing values detected. After splitting into 80% training and 20% testing sets, stationarity tests confirm the stationary nature of the dependent variable (Weekly_Sales). Time series decomposition reveals clear seasonality in the data. The SARIMA model with parameters (2, 0, 6) emerges as the optimal choice, achieving the lowest out-of-sample root mean squared error (RMSE) among various baseline and time series forecasting models.</p>
        </div>

        <div class="methods">
            <h2>Data & Methods</h2>
            <p><strong>Dataset:</strong> Weekly sales data from 45 Walmart stores with multiple features including Store, Dept, Temperature, Fuel_Price, Markdowns, CPI, Unemployment, Type, and Size.</p>
            
            <div class="chart">
                <p><strong>INSERT: Figure 1 from report</strong></p>
                <p>Histogram plots showing distribution of weekly sales and other features</p>
            </div>
            
            <p><strong>Pre-processing:</strong></p>
            <ul>
                <li>Data cleaning with verification of no missing values</li>
                <li>80/20 train-test split (337,256 training samples)</li>
                <li>Stationarity testing using ADF test (p-value: 2.68e-07) and KPSS test</li>
                <li>Feature selection & dimensionality reduction identified features with high VIF</li>
            </ul>
            
            <div class="chart">
                <p><strong>INSERT: Figure 2 from report</strong></p>
                <p>Weekly sales vs Week per Store line plots showing seasonal patterns</p>
            </div>
            
            <p><strong>Key Statistical Findings:</strong></p>
            <ul>
                <li>Strong seasonality (98.94% of variance)</li>
                <li>Minimal trend component (0.34%)</li>
                <li>Week 4 consistently showed highest sales across stores</li>
                <li>Holiday weeks showed significant sales increases (+1210 units)</li>
                <li>No significant autocorrelation was detected in the raw sales data</li>
            </ul>
        </div>

        <div class="results">
            <h2>Results</h2>
            
            <div class="chart">
                <p><strong>INSERT: Figure 3 from report</strong></p>
                <p>ACF/PACF Plots showing correlation patterns at different time lags</p>
            </div>
            
            <p><strong>Model Performance Comparison (RMSE):</strong></p>
            
            <div>
                <span class="metric">Average: 18610.89</span>
                <span class="metric">Naive: 25596.81</span>
                <span class="metric">Drift: 18664.09</span>
            </div>
            <div>
                <span class="metric">SES: 20467.38</span>
                <span class="metric">SARIMA(2,0,6): 18779.21</span>
                <span class="metric">OLS: 22208.08</span>
            </div>
            
            <div class="chart">
                <p><strong>INSERT: Figure 6 from report</strong></p>
                <p>Time Series Decomposition showing trend, seasonal, and residual components</p>
            </div>
            
            <p><strong>Linear Regression Results:</strong></p>
            <ul>
                <li>Low R² of 0.031 (adjusted R² = 0.022)</li>
                <li>Holiday weeks coefficient: +1210 units in sales</li>
                <li>High residual variance (493,198,620)</li>
                <li>Failed to capture time dependencies</li>
                <li>Q-statistic of 62.84 indicated autocorrelated residuals</li>
            </ul>
            
            <div class="chart">
                <p><strong>INSERT: Figure 4 from report</strong></p>
                <p>Correlation Heatmap showing relationships between variables</p>
            </div>
        </div>

        <div class="model-selection">
            <h2>Model Comparison</h2>
            
            <div class="model-card">
                <h3>OLS Regression</h3>
                <p>RMSE: 22208.08</p>
                <p>R²: 0.031</p>
                <p>Poor time series fit with high residual variance</p>
                <p>Failed to capture temporal dependencies</p>
            </div>
            
            <div class="model-card">
                <h3>SARIMA(3,0,8)</h3>
                <p>Log Likelihood: -4806941.09</p>
                <p>AIC: 9613906.18</p>
                <p>BIC: 9614037.61</p>
                <p>Good fit but more complex than necessary</p>
                <p>More parameters without significant improvement</p>
            </div>
            
            <div class="model-card best-model">
                <h3>SARIMA(2,0,6) - Best Model</h3>
                <p>Log Likelihood: -4807105.73</p>
                <p>AIC: 9614229.47</p>
                <p>BIC: 9614328.03</p>
                <p>Lowest out-of-sample RMSE: 18779.21</p>
                <p>Best balance of complexity and accuracy</p>
                <p>Effectively captured seasonal patterns</p>
            </div>
            
            <div class="chart">
                <p><strong>INSERT: Figure 8 from report</strong></p>
                <p>Preliminary Model Order Selection results</p>
            </div>
            
            <p><strong>Model Evaluation Process:</strong></p>
            <ul>
                <li>Preliminary order determination via GPAC analysis</li>
                <li>Parameter estimation using Levenberg-Marquardt algorithm</li>
                <li>Out-of-sample testing on 20% holdout data (84,314 samples)</li>
                <li>Comparison across multiple performance metrics (RMSE, AIC, BIC)</li>
                <li>Residual analysis for model diagnostics</li>
                <li>Ljung-Box test to check for remaining autocorrelation</li>
            </ul>
        </div>

        <div class="conclusion">
            <h2>Conclusion</h2>
            <p>This study successfully developed a time series forecasting model for Walmart's weekly sales data. The SARIMA(2,0,6) model emerged as the most effective approach, capturing the strong seasonal patterns that dominate the sales variations.</p>
            
            <div class="chart">
                <p><strong>INSERT: Figure 7 from report</strong></p>
                <p>Holt-Winters Forecasting visualization</p>
            </div>
            
            <p><strong>Key Findings:</strong></p>
            <ul>
                <li>Seasonality accounts for 98.94% of the sales variation, with minimal trend influence (0.34%)</li>
                <li>Week 4 consistently has the highest sales across most stores</li>
                <li>Holiday periods show significant sales increases</li>
                <li>Traditional regression models fail to capture the temporal dependencies in retail sales data</li>
                <li>SARIMA models outperform simpler forecasting approaches for this dataset</li>
            </ul>
            
            <div class="chart">
                <p><strong>INSERT: Figure 9 from report</strong></p>
                <p>Forecast Fit visualization showing model predictions vs actual data</p>
            </div>
            
            <p><strong>Business Impact:</strong> The SARIMA(2,0,6) model provides Walmart with a reliable forecasting tool for inventory planning and resource allocation, potentially improving operational efficiency and reducing costs associated with overstocking or stockouts.</p>
            
            <p><strong>Future Work:</strong></p>
            <ul>
                <li>Explore deep learning approaches (LSTM, Neural Networks) as shown in Figure 10</li>
                <li>Incorporate external factors such as promotions and competitor pricing</li>
                <li>Develop store-specific models for more localized forecasting</li>
                <li>Implement real-time forecasting updates with new data</li>
            </ul>
        </div>
    </div>
</body>
</html>
