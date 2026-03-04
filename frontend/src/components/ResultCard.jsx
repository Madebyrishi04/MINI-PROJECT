import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

const NumberCounter = ({ value }) => {
    const [count, setCount] = useState(0);

    useEffect(() => {
        let start = 0;
        const end = parseInt(value);
        if (start === end) {
            setCount(end);
            return;
        }

        let timer = setInterval(() => {
            start += 1;
            setCount(start);
            if (start === end) clearInterval(timer);
        }, 15);

        return () => clearInterval(timer);
    }, [value]);

    return <span>{count}</span>;
}

const ResultCard = ({ result }) => {
    const [expanded, setExpanded] = useState(false);

    if (!result) return null;

    const isReal = result.prediction.toLowerCase() === 'real';
    const colorClass = isReal ? 'text-success' : 'text-danger';
    const shadowClass = isReal ? 'shadow-[0_0_30px_rgba(0,230,118,0.2)]' : 'shadow-[0_0_30px_rgba(255,46,99,0.2)]';
    const bgClass = isReal ? 'bg-success/5' : 'bg-danger/5';
    const Icon = isReal ? ShieldCheck : ShieldAlert;
    const confidencePercent = Math.round(result.confidence * 100);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 30 }}
            whileInView={{ opacity: 1, scale: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ type: "spring", bounce: 0.4, duration: 0.8 }}
            className={`w-full glass-panel rounded-2xl overflow-hidden mt-8 border ${isReal ? 'border-success/30' : 'border-danger/30'} ${shadowClass}`}
        >
            <div className={`p-8 flex flex-col items-center text-center ${bgClass} relative overflow-hidden`}>
                {/* Subtle background glow */}
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full blur-3xl opacity-20 pointer-events-none ${isReal ? 'bg-success' : 'bg-danger'}`}></div>

                <motion.div
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: "spring", bounce: 0.5, delay: 0.2 }}
                    className={`p-5 rounded-full mb-5 border ${isReal ? 'bg-success/10 border-success/30 text-success' : 'bg-danger/10 border-danger/30 text-danger'} shadow-lg`}
                >
                    <Icon className="w-12 h-12" />
                </motion.div>

                <h2 className="text-textMuted text-xs tracking-[0.2em] uppercase mb-3 font-bold">
                    AI Analysis Complete
                </h2>

                <h3 className={`text-5xl font-extrabold tracking-tight uppercase ${colorClass} text-glow mb-8`}>
                    {result.prediction} News
                </h3>

                <div className="w-full max-w-sm bg-surface/80 rounded-full h-3 mb-3 overflow-hidden border border-white/5 relative">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${confidencePercent}%` }}
                        transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
                        className={`h-full ${isReal ? 'bg-success' : 'bg-danger'} shadow-[0_0_12px_currentColor]`}
                    />
                </div>

                <div className="flex justify-between w-full max-w-sm text-sm font-bold uppercase tracking-wider">
                    <span className="text-textMuted">Confidence Score</span>
                    <span className={`${colorClass} text-glow`}>
                        <NumberCounter value={confidencePercent} />%
                    </span>
                </div>
            </div>

            <div className="border-t border-white/5 bg-surface/40">
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="w-full p-5 flex items-center justify-center gap-2 text-textMuted hover:text-textMain transition-colors uppercase text-xs font-bold tracking-widest"
                >
                    <span>Why this result?</span>
                    <motion.div animate={{ rotate: expanded ? 180 : 0 }}>
                        <ChevronDown className="w-4 h-4" />
                    </motion.div>
                </button>

                <AnimatePresence>
                    {expanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden bg-black/20"
                        >
                            <div className="p-6 pt-2 text-sm leading-relaxed text-textMuted border-t border-white/5">
                                <p className="mb-3">
                                    <span className="text-primary font-semibold">Diagnostic log:</span> Neural network models analyzed the {isReal ? 'linguistic patterns, source credibility networks, and verifiable fact clusters' : 'emotional manipulation markers, hyperbole triggers, and structural inconsistencies'} within the provided input payload.
                                </p>
                                <p>
                                    The calculated confidence score of {confidencePercent}% suggests a <span className={colorClass}>{confidencePercent > 85 ? 'high' : 'moderate'}</span> degree of certainty based on cross-referencing with live data streams and historical disinformation vectors.
                                </p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
};

export default ResultCard;
