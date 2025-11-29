"""
Visualization Tools for MonteWalk
Provides flexible charting capabilities for market data, risk analysis, and backtesting.
"""

import io
import base64
import logging
from typing import List, Dict, Any, Optional, Union
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Set dark theme matching Gradio UI
plt.style.use('dark_background')
sns.set_palette(["#60a5fa", "#a855f7", "#ec4899", "#10b981", "#f59e0b"])

def _encode_figure(fig) -> str:
    """Convert matplotlib figure to base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0f172a')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def plot_line(
    data: Union[Dict[str, List], pd.DataFrame],
    x_label: str = "X",
    y_label: str = "Y",
    title: str = "Line Chart",
    labels: Optional[List[str]] = None
) -> str:
    """
    Create a line chart for time series or trend data.
    
    Args:
        data: Dictionary with 'x' and 'y' keys, or DataFrame
        x_label: Label for x-axis
        y_label: Label for y-axis
        title: Chart title
        labels: Legend labels for multiple lines
    
    Returns:
        Base64-encoded PNG image
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if isinstance(data, dict):
        if 'y' in data and isinstance(data['y'][0], list):
            # Multiple lines
            for i, y_data in enumerate(data['y']):
                label = labels[i] if labels and i < len(labels) else f"Series {i+1}"
                ax.plot(data['x'], y_data, linewidth=2, label=label, marker='o', markersize=4)
            ax.legend(loc='best', framealpha=0.9)
        else:
            # Single line
            ax.plot(data['x'], data['y'], linewidth=2, color='#60a5fa', marker='o', markersize=4)
    else:
        # DataFrame
        for col in data.columns[1:]:
            ax.plot(data.iloc[:, 0], data[col], linewidth=2, label=col, marker='o', markersize=4)
        if len(data.columns) > 2:
            ax.legend(loc='best', framealpha=0.9)
    
    ax.set_xlabel(x_label, fontsize=11, color='#e2e8f0')
    ax.set_ylabel(y_label, fontsize=11, color='#e2e8f0')
    ax.set_title(title, fontsize=14, fontweight='bold', color='#f8fafc', pad=20)
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.tick_params(colors='#94a3b8')
    
    return _encode_figure(fig)


def plot_candlestick(
    df: pd.DataFrame,
    title: str = "Candlestick Chart",
    volume: bool = True
) -> str:
    """
    Create a candlestick chart for OHLC data.
    
    Args:
        df: DataFrame with columns: Date, Open, High, Low, Close, Volume
        title: Chart title
        volume: Whether to show volume bars
    
    Returns:
        Base64-encoded PNG image
    """
    try:
        import mplfinance as mpf
        
        # Prepare data
        df_copy = df.copy()
        if 'Date' in df_copy.columns:
            df_copy.set_index('Date', inplace=True)
        df_copy.index = pd.to_datetime(df_copy.index)
        
        # Custom style matching our theme
        mc = mpf.make_marketcolors(
            up='#10b981', down='#ef4444',
            edge='inherit',
            wick='inherit',
            volume='#60a5fa',
            alpha=0.9
        )
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='--',
            gridcolor='#334155',
            facecolor='#0f172a',
            figcolor='#0f172a',
            edgecolor='#1e293b'
        )
        
        # Plot
        fig, axes = mpf.plot(
            df_copy,
            type='candle',
            style=s,
            volume=volume,
            title=title,
            ylabel='Price',
            ylabel_lower='Volume',
            figsize=(12, 8),
            returnfig=True
        )
        
        return _encode_figure(fig)
    except Exception as e:
        logger.error(f"Error creating candlestick chart: {e}")
        # Fallback to simple line chart
        return plot_line(
            {'x': list(range(len(df))), 'y': df['Close'].tolist()},
            x_label="Time",
            y_label="Price",
            title=title
        )


def plot_histogram(
    data: Union[List[float], np.ndarray],
    bins: int = 50,
    title: str = "Distribution",
    x_label: str = "Value",
    percentiles: Optional[List[float]] = None
) -> str:
    """
    Create a histogram for distribution analysis.
    
    Args:
        data: Array of values
        bins: Number of bins
        title: Chart title
        x_label: Label for x-axis
        percentiles: List of percentiles to mark (e.g., [5, 50, 95])
    
    Returns:
        Base64-encoded PNG image
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot histogram
    n, bins_edges, patches = ax.hist(
        data, bins=bins, color='#60a5fa', alpha=0.7, edgecolor='#94a3b8'
    )
    
    # Add percentile markers
    if percentiles:
        for p in percentiles:
            val = np.percentile(data, p)
            ax.axvline(val, color='#ec4899', linestyle='--', linewidth=2, alpha=0.8)
            ax.text(val, ax.get_ylim()[1] * 0.9, f'P{int(p)}: {val:.2f}',
                   rotation=90, va='top', ha='right', color='#ec4899', fontweight='bold')
    
    ax.set_xlabel(x_label, fontsize=11, color='#e2e8f0')
    ax.set_ylabel('Frequency', fontsize=11, color='#e2e8f0')
    ax.set_title(title, fontsize=14, fontweight='bold', color='#f8fafc', pad=20)
    ax.grid(True, alpha=0.2, axis='y', linestyle='--')
    ax.tick_params(colors='#94a3b8')
    
    return _encode_figure(fig)


def plot_scatter(
    x: List[float],
    y: List[float],
    title: str = "Scatter Plot",
    x_label: str = "X",
    y_label: str = "Y",
    trend_line: bool = True
) -> str:
    """
    Create a scatter plot for correlation analysis.
    
    Args:
        x: X-axis values
        y: Y-axis values
        title: Chart title
        x_label: Label for x-axis
        y_label: Label for y-axis
        trend_line: Whether to show trend line
    
    Returns:
        Base64-encoded PNG image
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot
    ax.scatter(x, y, alpha=0.6, s=50, color='#60a5fa', edgecolors='#94a3b8', linewidth=0.5)
    
    # Add trend line
    if trend_line and len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), color='#ec4899', linestyle='--', linewidth=2, alpha=0.8)
        
        # Calculate R²
        correlation = np.corrcoef(x, y)[0, 1]
        ax.text(0.05, 0.95, f'Correlation: {correlation:.3f}',
               transform=ax.transAxes, fontsize=10, color='#f8fafc',
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#1e293b', alpha=0.8))
    
    ax.set_xlabel(x_label, fontsize=11, color='#e2e8f0')
    ax.set_ylabel(y_label, fontsize=11, color='#e2e8f0')
    ax.set_title(title, fontsize=14, fontweight='bold', color='#f8fafc', pad=20)
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.tick_params(colors='#94a3b8')
    
    return _encode_figure(fig)


def plot_heatmap(
    matrix: Union[np.ndarray, pd.DataFrame],
    labels: Optional[List[str]] = None,
    title: str = "Heatmap"
) -> str:
    """
    Create a heatmap for correlation matrices.
    
    Args:
        matrix: 2D array or DataFrame
        labels: Row/column labels
        title: Chart title
    
    Returns:
        Base64-encoded PNG image
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if isinstance(matrix, pd.DataFrame):
        labels = matrix.columns.tolist()
        matrix = matrix.values
    
    # Create heatmap
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.tick_params(colors='#94a3b8')
    
    # Labels
    if labels:
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', color='#e2e8f0')
        ax.set_yticklabels(labels, color='#e2e8f0')
    
    # Annotate cells with values
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                         ha="center", va="center", color='#0f172a', fontsize=9, fontweight='bold')
    
    ax.set_title(title, fontsize=14, fontweight='bold', color='#f8fafc', pad=20)
    
    return _encode_figure(fig)


def plot_bar(
    categories: List[str],
    values: List[float],
    title: str = "Bar Chart",
    x_label: str = "Category",
    y_label: str = "Value",
    horizontal: bool = False
) -> str:
    """
    Create a bar chart for comparisons.
    
    Args:
        categories: Category labels
        values: Values for each category
        title: Chart title
        x_label: Label for x-axis
        y_label: Label for y-axis
        horizontal: Whether to make horizontal bars
    
    Returns:
        Base64-encoded PNG image
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#60a5fa' if v >= 0 else '#ef4444' for v in values]
    
    if horizontal:
        ax.barh(categories, values, color=colors, alpha=0.8, edgecolor='#94a3b8')
        ax.set_xlabel(y_label, fontsize=11, color='#e2e8f0')
        ax.set_ylabel(x_label, fontsize=11, color='#e2e8f0')
    else:
        ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='#94a3b8')
        ax.set_xlabel(x_label, fontsize=11, color='#e2e8f0')
        ax.set_ylabel(y_label, fontsize=11, color='#e2e8f0')
        plt.xticks(rotation=45, ha='right')
    
    ax.set_title(title, fontsize=14, fontweight='bold', color='#f8fafc', pad=20)
    ax.grid(True, alpha=0.2, axis='y' if not horizontal else 'x', linestyle='--')
    ax.tick_params(colors='#94a3b8')
    ax.axhline(0, color='#94a3b8', linewidth=0.8) if not horizontal else ax.axvline(0, color='#94a3b8', linewidth=0.8)
    
    return _encode_figure(fig)


def plot_data(
    data: Union[Dict, pd.DataFrame, List],
    chart_type: str = "auto",
    title: str = "Chart",
    **kwargs
) -> str:
    """
    Universal plotting function that auto-detects or accepts chart type.
    
    Args:
        data: Data to plot (format depends on chart_type)
        chart_type: Type of chart - "line", "candlestick", "histogram", "scatter", "heatmap", "bar", "auto"
        title: Chart title
        **kwargs: Additional arguments passed to specific plot functions
    
    Returns:
        Base64-encoded PNG image
    """
    try:
        # Auto-detect chart type
        if chart_type == "auto":
            if isinstance(data, pd.DataFrame) and all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
                chart_type = "candlestick"
            elif isinstance(data, (list, np.ndarray)) and isinstance(data[0], (int, float)):
                chart_type = "histogram"
            elif isinstance(data, dict):
                if 'x' in data and 'y' in data:
                    chart_type = "line"
                elif 'categories' in data and 'values' in data:
                    chart_type = "bar"
            else:
                chart_type = "line"
        
        # Route to specific function
        if chart_type == "line":
            return plot_line(data, title=title, **kwargs)
        elif chart_type == "candlestick":
            return plot_candlestick(data, title=title, **kwargs)
        elif chart_type == "histogram":
            return plot_histogram(data, title=title, **kwargs)
        elif chart_type == "scatter":
            return plot_scatter(data.get('x', []), data.get('y', []), title=title, **kwargs)
        elif chart_type == "heatmap":
            return plot_heatmap(data, title=title, **kwargs)
        elif chart_type == "bar":
            return plot_bar(data.get('categories', []), data.get('values', []), title=title, **kwargs)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
            
    except Exception as e:
        logger.error(f"Error creating chart: {e}", exc_info=True)
        return f"Error creating chart: {str(e)}"
