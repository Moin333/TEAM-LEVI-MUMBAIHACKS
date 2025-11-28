from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from loguru import logger

class AnalysisTools:
    """Statistical and ML analysis tools"""
    
    @staticmethod
    async def detect_outliers(
        df: pd.DataFrame,
        column: str,
        method: str = "iqr"
    ) -> Dict[str, Any]:
        """
        Detect outliers in data
        
        Methods: 'iqr', 'zscore'
        """
        try:
            series = df[column].dropna()
            
            if method == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = df[(df[column] < lower) | (df[column] > upper)]
            
            elif method == "zscore":
                z_scores = np.abs(stats.zscore(series))
                outliers = df[z_scores > 3]
            
            return {
                "outlier_count": len(outliers),
                "outlier_percentage": (len(outliers) / len(df)) * 100,
                "outlier_indices": outliers.index.tolist()
            }
            
        except Exception as e:
            logger.error(f"Outlier detection error: {str(e)}")
            raise
    
    @staticmethod
    async def correlation_analysis(
        df: pd.DataFrame,
        columns: List[str] = None
    ) -> Dict[str, Any]:
        """Calculate correlations between numeric columns"""
        try:
            if columns:
                df_numeric = df[columns]
            else:
                df_numeric = df.select_dtypes(include=[np.number])
            
            correlation_matrix = df_numeric.corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            "column1": correlation_matrix.columns[i],
                            "column2": correlation_matrix.columns[j],
                            "correlation": float(corr_value)
                        })
            
            return {
                "correlation_matrix": correlation_matrix.to_dict(),
                "strong_correlations": strong_correlations
            }
            
        except Exception as e:
            logger.error(f"Correlation analysis error: {str(e)}")
            raise
    
    @staticmethod
    async def segment_customers(
        df: pd.DataFrame,
        features: List[str],
        n_clusters: int = 3
    ) -> Dict[str, Any]:
        """
        Customer segmentation using K-means clustering
        
        Tool for agents to identify customer groups
        """
        try:
            # Prepare data
            X = df[features].dropna()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Cluster
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            df_copy = df.loc[X.index].copy()
            df_copy['cluster'] = clusters
            
            # Cluster profiles
            profiles = []
            for i in range(n_clusters):
                cluster_data = df_copy[df_copy['cluster'] == i]
                profile = {
                    "cluster_id": i,
                    "size": len(cluster_data),
                    "percentage": (len(cluster_data) / len(df_copy)) * 100,
                    "characteristics": {}
                }
                
                for feature in features:
                    profile["characteristics"][feature] = {
                        "mean": float(cluster_data[feature].mean()),
                        "median": float(cluster_data[feature].median())
                    }
                
                profiles.append(profile)
            
            return {
                "n_clusters": n_clusters,
                "cluster_assignments": clusters.tolist(),
                "profiles": profiles
            }
            
        except Exception as e:
            logger.error(f"Segmentation error: {str(e)}")
            raise
