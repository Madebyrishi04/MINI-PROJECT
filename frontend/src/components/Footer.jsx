import React from 'react';
import { motion } from 'framer-motion';

const Footer = () => {
    return (
        <motion.footer
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="w-full py-6 mt-16 text-center text-textMuted text-sm border-t border-white/5 glass-panel z-10 relative"
        >
            <div className="flex flex-col items-center justify-center gap-2">
                <p>&copy; {new Date().getFullYear()} FactFinder AI Systems. All rights reserved.</p>
                <p className="text-xs opacity-60">Powered by advanced neural networks for high-accuracy authenticity detection.</p>
            </div>
        </motion.footer>
    );
};

export default Footer;
