import React from 'react';
import { Loader2, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const AnalyzeButton = ({ isAnalyzing, onClick, disabled }) => {
    return (
        <motion.button
            whileHover={!disabled && !isAnalyzing ? { scale: 1.02 } : {}}
            whileTap={!disabled && !isAnalyzing ? { scale: 0.98 } : {}}
            onClick={onClick}
            disabled={disabled || isAnalyzing}
            className={`relative w-full py-4 mt-6 rounded-xl font-bold text-lg tracking-wide transition-all duration-300 overflow-hidden flex items-center justify-center gap-3
        ${disabled || isAnalyzing
                    ? 'bg-surface/50 text-textMuted cursor-not-allowed border border-white/5 opacity-70'
                    : 'bg-primary/10 text-primary border border-primary/50 shadow-[0_0_15px_rgba(0,229,255,0.3)] hover:shadow-[0_0_25px_rgba(0,229,255,0.6)] hover:bg-primary/20 cursor-pointer pointer-events-auto'
                }`}
        >
            {isAnalyzing ? (
                <>
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                    <span className="text-primary text-glow">Analyzing Authenticity...</span>
                </>
            ) : (
                <>
                    <Activity className={`w-6 h-6 ${disabled ? 'text-textMuted' : 'text-primary'}`} />
                    <span className={disabled ? '' : 'text-glow'}>Run AI Analysis</span>
                </>
            )}
        </motion.button>
    );
};

export default AnalyzeButton;
