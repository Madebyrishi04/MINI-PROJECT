import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import InputForm from './components/InputForm';
import AnalyzeButton from './components/AnalyzeButton';
import ResultCard from './components/ResultCard';
import ScrollReveal from './components/ScrollReveal';

function App() {
    const [inputData, setInputData] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [apiError, setApiError] = useState('');

    const handleInputReady = (data) => {
        setInputData(data);
        if (!data) {
            setResult(null);
            setApiError('');
        }
    };

    

    const handleAnalyze = async () => {
        console.log("BUTTON CLICKED");
        const handleInputReady = (data) => {
        console.log("APP RECEIVED:", data); // 🔥 ADD
        setInputData(data);
        };
        if (!inputData) return;

        setIsAnalyzing(true);
        setApiError('');
        setResult(null);

        // Simulate API call processing layout transition
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

        try {
            let body;
            let headers = {};

            if (inputData.type === 'image') {
                const formData = new FormData();
                formData.append('image', inputData.data);
                body = formData;
                // fetch handles multipart boundary automatically when body is FormData
            } else if (inputData.type === 'text') {
                body = JSON.stringify({ text: inputData.data });
                headers['Content-Type'] = 'application/json';
            } else if (inputData.type === 'url') {
                body = JSON.stringify({ url: inputData.data });
                headers['Content-Type'] = 'application/json';
            }

            let url = "";

            if (inputData.type === "image") {
                url = "http://127.0.0.1:5000/predict_image";
            } else if (inputData.type === "text") {
                url = "http://127.0.0.1:5000/predict_text";
            } else if (inputData.type === "url") {
                url = "http://127.0.0.1:5000/predict_url";
            }

            const response = await fetch(url, {
                method: "POST",
                headers: Object.keys(headers).length > 0 ? headers : undefined,
                body
            });

            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }

            const data = await response.json();
            setResult(data);
            setIsAnalyzing(false);
        } catch (err) {
            console.warn("Backend not detected or request failed, using demo fallback:", err);

            // Fallback response to ensure the frontend demo works smoothly without a backend
            setTimeout(() => {
                const isReal = Math.random() > 0.5;
                setResult({
                    prediction: isReal ? "Real" : "Fake",
                    confidence: parseFloat((Math.random() * 0.3 + 0.65).toFixed(2)) // Generates a confidence between 0.65 and 0.95
                });
                setIsAnalyzing(false);
                // We set a small toast or warning indicating it's a mock evaluation
                setApiError('Unable to reach /predict API. Displaying simulated results.');
            }, 2000);
        }
    };

    return (
        <div className="min-h-screen flex flex-col relative w-full overflow-hidden font-sans">
            <div className="bg-gradient-dynamic"></div>
            <div className="orb orb-1"></div>
            <div className="orb orb-2"></div>
            <div className="orb orb-3"></div>
            <div className="bg-grid"></div>

            <Navbar />

            <main className="flex-1 w-full max-w-4xl mx-auto px-6 pt-32 pb-12 flex flex-col items-center relative z-10">
                <div className="text-center w-full mb-12">
                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight mb-4 text-glow flicker-effect">
                        AI Powered News <br className="hidden md:block" />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primaryDark text-glow-none">Authenticity Checker</span>
                    </h1>
                    <p className="text-textMuted text-lg max-w-2xl mx-auto leading-relaxed">
                        Upload article text, provide a URL, or drop an image to leverage advanced neural network verification against known disinformation patterns.
                    </p>
                </div>

                <div className="w-full max-w-2xl bg-surface/30 p-1 rounded-3xl border border-white/5 shadow-2xl backdrop-blur-sm">
                    <div className="bg-surface/50 p-6 md:p-8 rounded-[22px] border border-white/5">
                        <InputForm onInputReady={handleInputReady} />
                        <AnalyzeButton
                            isAnalyzing={isAnalyzing}
                            onClick={handleAnalyze}
                            disabled={false}
                        />
                    </div>
                </div>

                <AnimatePresence mode="wait">
                    {apiError && result && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-6 w-full max-w-2xl bg-yellow-500/10 border border-yellow-500/30 text-yellow-500/90 p-4 rounded-xl flex items-center justify-center gap-3 text-sm"
                        >
                            <AlertCircle className="w-5 h-5" />
                            <span>{apiError}</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                <AnimatePresence mode="wait">
                    {result && !isAnalyzing && (
                        <div className="w-full max-w-2xl">
                            <ResultCard result={result} />
                        </div>
                    )}
                </AnimatePresence>
            </main>

            <Footer />
        </div>
    );
}

export default App;
