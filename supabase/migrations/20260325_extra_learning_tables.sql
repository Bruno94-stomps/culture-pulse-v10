
-- 20260325_feedback_and_realtime_setup.sql
-- Extra learning tables for FeedbackEngine and RealTimeLearningEngine

-- Table for Individual Signal Feedback (FeedbackEngine)
CREATE TABLE IF NOT EXISTS signal_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id TEXT NOT NULL,
    rating FLOAT NOT NULL,
    effectiveness FLOAT,
    features FLOAT8[], -- Vector for RandomForest features
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_signal_id ON signal_feedback(signal_id);

-- Table for Model Weights (RealTimeLearningEngine)
CREATE TABLE IF NOT EXISTS model_weights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    weights JSONB NOT NULL,
    performance_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Analysis Performance (RealTimeLearningEngine)
CREATE TABLE IF NOT EXISTS analysis_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id TEXT NOT NULL,
    predicted_scores JSONB,
    actual_performance JSONB,
    accuracy_metrics JSONB,
    context JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_performance_id ON analysis_performance(analysis_id);
