import React from 'react';
import { Search } from 'lucide-react';
import { motion } from 'framer-motion';

const Navbar = () => {
    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="fixed top-0 left-0 w-full z-50 glass-panel border-b-0 border-white/5 py-4 px-6 md:px-12 flex items-center justify-between"
        >
            <div className="flex items-center gap-3">
                <motion.div
                    whileHover={{ rotate: 90 }}
                    transition={{ duration: 0.3 }}
                    className="p-2 bg-primary/10 rounded-xl border border-primary/20"
                >
                    <Search className="w-5 h-5 text-primary" />
                </motion.div>
                <h1 className="text-xl font-bold tracking-wider text-textMain select-none">
                    Fact<span className="text-primary text-glow drop-shadow-[0_0_8px_rgba(0,229,255,0.8)]">Finder</span>
                </h1>
            </div>

            <div className="hidden md:flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-success animate-pulse shadow-[0_0_8px_rgba(0,230,118,0.8)]"></span>
                <span className="text-xs text-textMuted uppercase tracking-widest font-semibold">AI System Online</span>
            </div>
        </motion.nav>
    );
};

export default Navbar;
