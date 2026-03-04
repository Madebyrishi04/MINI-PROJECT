import React from 'react';
import { motion } from 'framer-motion';

const ScrollReveal = ({ children, className, stagger = false, delay = 0 }) => {
    const containerVariants = {
        hidden: { opacity: 0, y: 50 },
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                duration: 0.8,
                ease: [0.16, 1, 0.3, 1],
                delay: delay,
                when: "beforeChildren",
                staggerChildren: stagger ? 0.2 : 0,
            }
        }
    };

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className={className}
        >
            {children}
        </motion.div>
    );
};

export const ScrollRevealItem = ({ children, className }) => {
    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] }
        }
    };

    return (
        <motion.div variants={itemVariants} className={className}>
            {children}
        </motion.div>
    );
};

export default ScrollReveal;
