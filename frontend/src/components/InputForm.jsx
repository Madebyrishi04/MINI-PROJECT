import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, Type, X, UploadCloud } from 'lucide-react';
import { ScrollRevealItem } from './ScrollReveal';

const InputForm = ({ onInputReady }) => {
    const [activeInput, setActiveInput] = useState(null); // 'text', 'url', 'image', or null
    const [text, setText] = useState('');
    const [url, setUrl] = useState('');
    const [image, setImage] = useState(null);
    const [error, setError] = useState('');
    const [isDragging, setIsDragging] = useState(false);

    const fileInputRef = useRef(null);

    const handleClear = () => {
        setActiveInput(null);
        setText('');
        setUrl('');
        setImage(null);
        setError('');
        onInputReady(null);
    };

    const handleTextChange = (e) => {
        const val = e.target.value;
        if (activeInput && activeInput !== 'text') {
            setError('Only one input type allowed at a time. Clear current input first.');
            return;
        }
        setText(val);
        if (val.trim()) {
            setActiveInput('text');
            onInputReady({ type: 'text', data: val });
        } else {
            setActiveInput(null);
            onInputReady(null);
        }
    };

    const handleUrlChange = (e) => {
        const val = e.target.value;
        if (activeInput && activeInput !== 'url') {
            setError('Only one input type allowed at a time. Clear current input first.');
            return;
        }
        setUrl(val);
        if (val.trim()) {
            setActiveInput('url');
            onInputReady({ type: 'url', data: val });
        } else {
            setActiveInput(null);
            onInputReady(null);
        }
    };

    const processFile = (file) => {
    console.log("FILE SELECTED:", file); // 🔥 ADD

    if (activeInput && activeInput !== 'image') {
        setError('Only one input type allowed at a time. Clear current input first.');
        return;
    }

    if (file && file.type.startsWith('image/')) {
        setImage(file);
        setActiveInput('image');

        console.log("CALLING onInputReady"); // 🔥 ADD

        onInputReady({ type: 'image', data: file });

        setError('');
    } else {
        setError('Please upload a valid image file.');
    }
};

    const handleDragOver = (e) => {
        e.preventDefault();
        if (!activeInput || activeInput === 'image') {
            setIsDragging(true);
        }
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    };

    const containerVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.6, staggerChildren: 0.1 } }
    };

    const getOverlayBlur = (type) => {
    if (activeInput && activeInput !== type)
        return 'opacity-40 grayscale'; // ❌ REMOVE pointer-events-none
    return '';
};

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            className="w-full space-y-4 relative"
        >
            <ScrollRevealItem className="flex justify-between items-center mb-2 px-1">
                <h2 className="text-lg font-semibold text-textMain tracking-wide">Select Data Source</h2>
                {activeInput && (
                    <button
                        onClick={handleClear}
                        className="text-xs flex items-center gap-1 text-danger hover:text-danger/80 transition-colors uppercase tracking-wider font-bold"
                    >
                        <X className="w-4 h-4" /> Clear Input
                    </button>
                )}
            </ScrollRevealItem>

            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, height: 0, y: -10 }}
                        animate={{ opacity: 1, height: 'auto', y: 0 }}
                        exit={{ opacity: 0, height: 0, y: -10 }}
                        className="text-danger text-sm bg-danger/10 border border-danger/30 p-3 rounded-lg flex items-center gap-2 mb-4"
                    >
                        <span className="w-2 h-2 rounded-full bg-danger animate-pulse shadow-[0_0_8px_rgba(255,46,99,0.8)]"></span>
                        {error}
                    </motion.div>
                )}
            </AnimatePresence>

            <ScrollRevealItem className={`glass-panel p-5 rounded-2xl transition-all duration-300 ${getOverlayBlur('text')} focus-within:border-primary/50 focus-within:shadow-[0_0_15px_rgba(0,229,255,0.1)]`}>
                <div className="flex items-center gap-2 mb-3 text-primary">
                    <Type className="w-5 h-5" />
                    <span className="font-semibold uppercase tracking-wider text-sm">Direct Text</span>
                </div>
                <textarea
                    value={text}
                    onChange={handleTextChange}
                    placeholder="Paste article text here for analysis..."
                    className="w-full bg-surface/40 hover:bg-surface/60 border border-white/5 rounded-xl p-4 text-textMain placeholder:text-textMuted focus:outline-none focus:border-primary/50 transition-all resize-none h-32"
                />
            </ScrollRevealItem>

            <ScrollRevealItem className={`glass-panel p-5 rounded-2xl transition-all duration-300 ${getOverlayBlur('url')} focus-within:border-primary/50 focus-within:shadow-[0_0_15px_rgba(0,229,255,0.1)]`}>
                <div className="flex items-center gap-2 mb-3 text-primary">
                    <Link className="w-5 h-5" />
                    <span className="font-semibold uppercase tracking-wider text-sm">Article URL</span>
                </div>
                <input
                    type="url"
                    value={url}
                    onChange={handleUrlChange}
                    placeholder="https://example.com/news-article..."
                    className="w-full bg-surface/40 hover:bg-surface/60 border border-white/5 rounded-xl p-4 text-textMain placeholder:text-textMuted focus:outline-none focus:border-primary/50 transition-all font-mono text-sm"
                />
            </ScrollRevealItem>

            <div
    className={`glass-panel p-8 rounded-2xl transition-all duration-300 border-dashed border-2 flex flex-col items-center justify-center text-center cursor-pointer min-h-[160px]
    ${isDragging ? 'border-primary bg-primary/10 shadow-[0_0_20px_rgba(0,229,255,0.2)]' : 'border-white/10 hover:border-primary/30 hover:bg-surface/60'} 
    ${getOverlayBlur('image')}`}
    onDragOver={handleDragOver}
    onDragLeave={handleDragLeave}
    onDrop={handleDrop}
    onClick={() => fileInputRef.current?.click()}
>
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="image/*"
                    onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                            processFile(e.target.files[0]);
                        }
                    }}
                />
                {image ? (
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="flex flex-col items-center gap-3"
                    >
                        <div className="w-20 h-20 rounded-xl overflow-hidden border-2 border-primary/50 shadow-[0_0_15px_rgba(0,229,255,0.3)]">
                            <img src={URL.createObjectURL(image)} alt="Preview" className="w-full h-full object-cover" />
                        </div>
                        <span className="text-sm font-medium text-primary truncate max-w-[250px] bg-primary/10 px-3 py-1 rounded-full">{image.name}</span>
                    </motion.div>
                ) : (
                    <div className="flex flex-col items-center gap-4">
                        <div className="p-4 bg-white/5 rounded-full group-hover:bg-primary/10 transition-colors">
                            <UploadCloud className="w-8 h-8 text-textMuted group-hover:text-primary transition-colors" />
                        </div>
                        <div>
                            <p className="font-semibold text-textMain tracking-wide">Drag & Drop Image Evidence</p>
                            <p className="text-xs text-textMuted mt-2 uppercase tracking-widest">or click to browse files</p>
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    );
};

export default InputForm;
