# Salesforce NBA CrewAI Architecture

## Overview

The Salesforce NBA application uses CrewAI to orchestrate multiple AI agents that collaborate to analyze Salesforce accounts and generate actionable recommendations.

## Architecture Diagram
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Streamlit UI │────▶│ Workflow │────▶│ CrewAI │
│ │ │ Manager │ │ Agents │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Salesforce │ │ LLM Provider │ │ Tools & │
│ Integration │ │ (OpenAI/ │ │ Utilities │
│ │ │ Gemini) │ │ │
└─────────────────┘ └─────────────────┘ └─────────────────┘


## Key Components

### 1. Agents
- **Data Analyst**: Analyzes account data and identifies patterns
- **Risk Analyst**: Assesses risks and account health
- **Strategist**: Develops strategic recommendations
- **Execution Planner**: Creates detailed action plans

### 2. Crews
- **Analysis Crew**: Data Analyst + Risk Analyst
- **Strategy Crew**: Strategist + Data Analyst
- **Execution Crew**: Execution Planner

### 3. Workflows
- **NBA Workflow**: Orchestrates the complete analysis → recommendation → planning flow

## Data Flow

1. User inputs Salesforce Account ID
2. Salesforce Client fetches comprehensive account data
3. Analysis Crew analyzes the data
4. Strategy Crew generates recommendations
5. User selects a recommendation
6. Execution Crew creates action plan
7. Actions are executed in Salesforce

## Design Patterns

- **Factory Pattern**: Agent and Task factories
- **Repository Pattern**: Data access layer
- **Strategy Pattern**: LLM provider selection
- **Observer Pattern**: Event-driven UI updates