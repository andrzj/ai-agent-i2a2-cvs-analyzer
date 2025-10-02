"""
Relationship Analysis Tools

Tools for analyzing correlations and relationships between variables.
"""

import pandas as pd
import numpy as np
from typing import Optional
from langchain.tools import Tool
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from scipy.stats import pearsonr, spearmanr

from .data_description import get_dataframe, _data_processor


# ============================================================
# Tool 12: Calculate Correlation
# ============================================================

def calculate_correlation(input_str: str) -> str:
    """Calculate correlation matrix for numerical columns."""
    try:
        df = get_dataframe()
        
        if input_str.strip():
            columns = [c.strip() for c in input_str.split(',')]
            # Validate columns
            invalid_cols = [c for c in columns if c not in df.columns]
            if invalid_cols:
                return f"Error: Columns not found: {', '.join(invalid_cols)}"
        else:
            # Get all numerical columns
            type_info = _data_processor.analyze_data_types(df)
            columns = [col for col, info in type_info.items() if info['semantic_type'] == 'numerical']
        
        if len(columns) < 2:
            return "Error: Need at least 2 numerical columns for correlation analysis"
        
        # Select only numerical columns
        df_corr = df[columns].select_dtypes(include=[np.number])
        
        if df_corr.shape[1] < 2:
            return "Error: Not enough numerical columns"
        
        # Calculate correlation matrix
        corr_matrix = df_corr.corr()
        
        result = f"🔗 Correlation Analysis:\n\n"
        result += f"**Columns analyzed:** {len(df_corr.columns)}\n"
        result += f"**Method:** Pearson correlation\n\n"
        
        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:  # Strong correlation threshold
                    strong_corr.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        corr_val
                    ))
        
        if strong_corr:
            strong_corr.sort(key=lambda x: abs(x[2]), reverse=True)
            result += "**Strong Correlations (|r| > 0.5):**\n"
            for col1, col2, corr_val in strong_corr[:10]:
                direction = "positive" if corr_val > 0 else "negative"
                strength = "very strong" if abs(corr_val) > 0.8 else "strong"
                result += f"  • {col1} ↔ {col2}: {corr_val:.3f} ({strength} {direction})\n"
            
            if len(strong_corr) > 10:
                result += f"  ... and {len(strong_corr) - 10} more\n"
        else:
            result += "No strong correlations found (all |r| ≤ 0.5)\n"
        
        result += "\n**Full Correlation Matrix:**\n"
        result += corr_matrix.to_string()
        
        result += "\n\n**Interpretation Guide:**\n"
        result += "  • |r| > 0.7: Strong correlation\n"
        result += "  • 0.5 < |r| ≤ 0.7: Moderate correlation\n"
        result += "  • 0.3 < |r| ≤ 0.5: Weak correlation\n"
        result += "  • |r| ≤ 0.3: Very weak/no correlation\n"
        
        return result
        
    except Exception as e:
        return f"Error calculating correlation: {str(e)}"


calculate_correlation_tool = Tool(
    name="calculate_correlation",
    func=calculate_correlation,
    description="""Calcule a matriz de correlação de Pearson para colunas numéricas.
    A entrada deve ser nomes de colunas separados por vírgula, ou vazio para todas as colunas numéricas.
    Exemplo: "age,salary,experience" ou "" para todas as colunas numéricas"""
)


# ============================================================
# Tool 13: Analyze Variable Relationships
# ============================================================

def analyze_variable_relationships(input_str: str) -> str:
    """Analyze relationship between two specific variables."""
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        if len(parts) != 2:
            return "Error: Input should be 'column1,column2'"
        
        col1, col2 = parts
        
        if col1 not in df.columns:
            return f"Error: Column '{col1}' not found"
        if col2 not in df.columns:
            return f"Error: Column '{col2}' not found"
        
        # Get data
        df_temp = df[[col1, col2]].dropna()
        
        if len(df_temp) < 2:
            return "Error: Not enough data points for analysis"
        
        type1 = _data_processor.detect_column_type(df_temp[col1])
        type2 = _data_processor.detect_column_type(df_temp[col2])
        
        result = f"🔗 Relationship Analysis: '{col1}' vs '{col2}'\n\n"
        result += f"**{col1}:** {type1}\n"
        result += f"**{col2}:** {type2}\n"
        result += f"**Valid data points:** {len(df_temp):,}\n\n"
        
        # Both numerical
        if type1 == 'numerical' and type2 == 'numerical':
            # Pearson correlation
            pearson_r, pearson_p = pearsonr(df_temp[col1], df_temp[col2])
            
            # Spearman correlation (for non-linear relationships)
            spearman_r, spearman_p = spearmanr(df_temp[col1], df_temp[col2])
            
            result += "**Correlation Analysis:**\n"
            result += f"  • Pearson correlation: {pearson_r:.3f} (p-value: {pearson_p:.4f})\n"
            result += f"  • Spearman correlation: {spearman_r:.3f} (p-value: {spearman_p:.4f})\n\n"
            
            if pearson_p < 0.05:
                if abs(pearson_r) > 0.7:
                    strength = "strong"
                elif abs(pearson_r) > 0.5:
                    strength = "moderate"
                elif abs(pearson_r) > 0.3:
                    strength = "weak"
                else:
                    strength = "very weak"
                
                direction = "positive" if pearson_r > 0 else "negative"
                result += f"**Interpretation:** There is a {strength} {direction} linear relationship.\n"
                
                if pearson_r > 0:
                    result += f"  • As {col1} increases, {col2} tends to increase\n"
                else:
                    result += f"  • As {col1} increases, {col2} tends to decrease\n"
            else:
                result += "**Interpretation:** No significant linear relationship detected.\n"
            
            # Check for non-linear relationship
            if abs(spearman_r - pearson_r) > 0.2:
                result += "\n⚠️ Spearman differs from Pearson - possible non-linear relationship\n"
        
        # One numerical, one categorical
        elif (type1 == 'numerical' and type2 == 'categorical') or \
             (type1 == 'categorical' and type2 == 'numerical'):
            
            if type1 == 'categorical':
                cat_col, num_col = col1, col2
            else:
                cat_col, num_col = col2, col1
            
            result += "**Group Statistics:**\n\n"
            
            grouped = df_temp.groupby(cat_col)[num_col].agg(['count', 'mean', 'std', 'min', 'max'])
            
            for category in grouped.index[:10]:  # Show first 10 categories
                row = grouped.loc[category]
                result += f"**{category}:**\n"
                result += f"  • Count: {int(row['count']):,}\n"
                result += f"  • Mean: {row['mean']:.2f}\n"
                result += f"  • Std: {row['std']:.2f}\n"
                result += f"  • Range: [{row['min']:.2f}, {row['max']:.2f}]\n\n"
            
            if len(grouped) > 10:
                result += f"... and {len(grouped) - 10} more categories\n\n"
            
            # ANOVA-like interpretation
            overall_mean = df_temp[num_col].mean()
            group_means = grouped['mean']
            variation = ((group_means - overall_mean) ** 2).sum()
            
            if variation > df_temp[num_col].var():
                result += f"**Interpretation:** {cat_col} appears to influence {num_col} values significantly.\n"
            else:
                result += f"**Interpretation:** {cat_col} has minimal influence on {num_col} values.\n"
        
        # Both categorical
        elif type1 == 'categorical' and type2 == 'categorical':
            crosstab = pd.crosstab(df_temp[col1], df_temp[col2])
            
            result += "**Crosstabulation (first 10x10):**\n\n"
            result += crosstab.iloc[:10, :10].to_string()
            
            if crosstab.shape[0] > 10 or crosstab.shape[1] > 10:
                result += "\n\n(Showing subset of full table)\n"
        
        else:
            result += "Relationship analysis not available for these column types.\n"
        
        return result
        
    except Exception as e:
        return f"Error analyzing relationship: {str(e)}"


analyze_variable_relationships_tool = Tool(
    name="analyze_variable_relationships",
    func=analyze_variable_relationships,
    description="""Analise o relacionamento entre duas variáveis específicas (correlação, diferenças de grupo, etc.).
    A entrada deve ser 'column1,column2' (separado por vírgula).
    Exemplo: "age,salary" ou "department,income" """
)


# ============================================================
# Tool 14: Identify Influential Variables
# ============================================================

def identify_influential_variables(input_str: str) -> str:
    """Identify which variables have the most influence on a target variable."""
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        target_col = parts[0]
        
        if target_col not in df.columns:
            return f"Error: Target column '{target_col}' not found"
        
        if len(parts) > 1:
            feature_cols = parts[1:]
        else:
            # Use all numerical columns except target
            type_info = _data_processor.analyze_data_types(df)
            feature_cols = [
                col for col, info in type_info.items() 
                if info['semantic_type'] == 'numerical' and col != target_col
            ]
        
        if not feature_cols:
            return "Error: No feature columns available for analysis"
        
        # Prepare data
        df_temp = df[[target_col] + feature_cols].dropna()
        
        if len(df_temp) < 10:
            return "Error: Not enough data points for feature importance analysis"
        
        target_type = _data_processor.detect_column_type(df_temp[target_col])
        
        result = f"🎯 Feature Importance Analysis:\n\n"
        result += f"**Target variable:** {target_col} ({target_type})\n"
        result += f"**Feature variables:** {len(feature_cols)}\n"
        result += f"**Data points:** {len(df_temp):,}\n\n"
        
        X = df_temp[feature_cols]
        y = df_temp[target_col]
        
        # Use Random Forest for feature importance
        if target_type == 'numerical':
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X, y)
            score = model.score(X, y)
            result += f"**Model R² score:** {score:.3f}\n\n"
        else:
            # For categorical, try to use classifier
            try:
                model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
                model.fit(X, y)
                score = model.score(X, y)
                result += f"**Model accuracy score:** {score:.3f}\n\n"
            except:
                return "Error: Cannot build model for this target type"
        
        # Get feature importances
        importances = model.feature_importances_
        feature_importance = list(zip(feature_cols, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        result += "**Feature Importance Ranking:**\n\n"
        
        for i, (feature, importance) in enumerate(feature_importance, 1):
            percentage = importance * 100
            bar = "█" * int(percentage / 2)  # Visual bar
            result += f"{i}. {feature}: {importance:.4f} ({percentage:.1f}%) {bar}\n"
        
        result += "\n**Interpretation:**\n"
        top_3 = feature_importance[:3]
        top_3_names = [f[0] for f in top_3]
        total_importance = sum([f[1] for f in top_3])
        
        result += f"  • Top 3 features ({', '.join(top_3_names)}) account for {total_importance*100:.1f}% of influence\n"
        
        if feature_importance[0][1] > 0.5:
            result += f"  • {feature_importance[0][0]} is the dominant influencing factor\n"
        elif total_importance > 0.8:
            result += "  • A few features dominate the influence\n"
        else:
            result += "  • Influence is distributed across multiple features\n"
        
        return result
        
    except Exception as e:
        return f"Error identifying influential variables: {str(e)}"


identify_influential_variables_tool = Tool(
    name="identify_influential_variables",
    func=identify_influential_variables,
    description="""Identifique quais variáveis têm mais influência em uma variável alvo usando importância de features.
    A entrada deve ser 'target_column' ou 'target_column,feature1,feature2,...'
    Exemplo: "salary" ou "price,age,experience,education" """
)
