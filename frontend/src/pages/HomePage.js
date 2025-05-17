import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../components/Button';
import { FaTshirt, FaMagic, FaShoppingBag } from 'react-icons/fa';

const HomePage = () => {
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        staggerChildren: 0.3,
        delayChildren: 0.2
      }
    }
  };
  
  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  const features = [
    {
      icon: <FaTshirt className="h-8 w-8 text-accent" />,
      title: "Try Before You Buy",
      description: "See how clothes look on you without physically trying them on"
    },
    {
      icon: <FaMagic className="h-8 w-8 text-accent" />,
      title: "AI-Powered Technology",
      description: "Our advanced AI ensures realistic virtual try-ons with accurate sizing and fit"
    },
    {
      icon: <FaShoppingBag className="h-8 w-8 text-accent" />,
      title: "Works on Any Store",
      description: "Use our extension with your favorite online clothing retailers"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-background-light text-white">
      {/* Hero Section */}
      <motion.section 
        className="pt-20 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto"
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <motion.h1 
              className="text-4xl sm:text-5xl font-bold font-heading leading-tight"
              variants={itemVariants}
            >
              Virtual Try-On for <span className="text-accent">Any Clothing</span> Online
            </motion.h1>
            
            <motion.p 
              className="mt-4 text-lg text-gray-300 max-w-lg"
              variants={itemVariants}
            >
              Try clothes on virtually before purchasing. Our Chrome extension works with any e-commerce site to let you see how items look on you.
            </motion.p>
            
            <motion.div 
              className="mt-8 flex flex-col sm:flex-row gap-4"
              variants={itemVariants}
            >
              <Link to="/app">
                <Button size="lg" variant="primary">
                  Try It Now
                </Button>
              </Link>
              <Button size="lg" variant="outline">
                Learn More
              </Button>
            </motion.div>
          </div>
          
          <motion.div
            className="rounded-lg overflow-hidden shadow-2xl"
            variants={itemVariants}
          >
            <img 
              src="https://images.unsplash.com/photo-1595341888016-a392ef81b7de?q=80&w=1000&auto=format&fit=crop" 
              alt="Virtual Try On Demo" 
              className="w-full h-auto object-cover"
            />
          </motion.div>
        </div>
      </motion.section>

      {/* Features Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div 
              key={index}
              className="bg-background p-6 rounded-lg shadow-lg"
              whileHover={{ y: -5, boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)" }}
              transition={{ duration: 0.2 }}
            >
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-300">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="bg-primary/20 rounded-lg p-8 sm:p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Revolutionize Your Online Shopping?</h2>
          <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
            Try our virtual fitting room today and never worry about ordering the wrong size or style again.
          </p>
          <Link to="/app">
            <Button size="lg" variant="accent">Get Started</Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
