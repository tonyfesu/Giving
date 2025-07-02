import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Hero Section Component
const HeroSection = () => {
  return (
    <div className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white py-20 px-4">
      <div className="absolute inset-0 bg-black opacity-20"></div>
      <div className="relative max-w-6xl mx-auto text-center">
        <div className="mb-8">
          <img 
            src="https://images.unsplash.com/photo-1469571486292-0ba58a3f068b" 
            alt="Social Impact" 
            className="mx-auto w-32 h-32 rounded-full object-cover shadow-xl border-4 border-white"
          />
        </div>
        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Turn Every Sale Into 
          <span className="text-yellow-300"> Social Impact</span>
        </h1>
        <p className="text-xl md:text-2xl mb-8 opacity-90 max-w-3xl mx-auto">
          ImpactLink helps businesses drive meaningful social change through commerce. 
          Connect your sales to causes you care about and show customers the impact of their purchases.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="bg-yellow-400 text-black px-8 py-4 rounded-full font-semibold text-lg hover:bg-yellow-300 transform hover:scale-105 transition-all shadow-lg">
            Start Making Impact
          </button>
          <button className="border-2 border-white text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white hover:text-purple-600 transition-all">
            See How It Works
          </button>
        </div>
      </div>
    </div>
  );
};

// Features Section
const FeaturesSection = () => {
  const features = [
    {
      title: "Impact Allocation Engine",
      description: "Choose causes you care about and set what percentage of each sale goes to social impact",
      icon: "🎯",
      color: "bg-green-100 border-green-200"
    },
    {
      title: "Real-time Impact Tracking",
      description: "See exactly how much impact your business is creating with transparent, real-time dashboards",
      icon: "📊",
      color: "bg-blue-100 border-blue-200"
    },
    {
      title: "Customer Engagement",
      description: "Show customers the impact of their purchases and build stronger relationships through shared values",
      icon: "❤️",
      color: "bg-red-100 border-red-200"
    },
    {
      title: "Verified Impact",
      description: "All contributions are tracked transparently with detailed reporting on how funds are being used",
      icon: "✅",
      color: "bg-purple-100 border-purple-200"
    }
  ];

  return (
    <div className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            How ImpactLink Works
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Simple, transparent, and powerful tools to integrate social impact into your business operations
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className={`${feature.color} border-2 rounded-xl p-6 text-center hover:shadow-lg transition-all`}>
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Business Dashboard Component
const BusinessDashboard = ({ business, onTransactionCreate }) => {
  const [causes, setCauses] = useState([]);
  const [allocations, setAllocations] = useState({});
  const [dashboard, setDashboard] = useState(null);
  const [transactionAmount, setTransactionAmount] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [showTransactionForm, setShowTransactionForm] = useState(false);

  useEffect(() => {
    if (business?.id) {
      fetchCauses();
      fetchDashboard();
      // Initialize allocations from business data
      setAllocations(business.impact_allocations || {});
    }
  }, [business]);

  const fetchCauses = async () => {
    try {
      const response = await axios.get(`${API}/causes`);
      setCauses(response.data);
    } catch (error) {
      console.error("Error fetching causes:", error);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/impact/dashboard/${business.id}`);
      setDashboard(response.data);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
    }
  };

  const handleAllocationChange = (causeId, percentage) => {
    setAllocations(prev => ({
      ...prev,
      [causeId]: percentage
    }));
  };

  const saveAllocations = async () => {
    try {
      const allocationList = Object.entries(allocations)
        .filter(([_, percentage]) => percentage > 0)
        .map(([cause_id, percentage]) => ({ cause_id, percentage: parseFloat(percentage) }));

      await axios.put(`${API}/businesses/${business.id}/impact-allocation`, allocationList);
      alert("Impact allocation saved successfully!");
      fetchDashboard();
    } catch (error) {
      console.error("Error saving allocations:", error);
      alert("Error saving allocations: " + (error.response?.data?.detail || error.message));
    }
  };

  const createTransaction = async () => {
    try {
      const transaction = {
        business_id: business.id,
        amount: parseFloat(transactionAmount),
        customer_name: customerName || undefined
      };

      const response = await axios.post(`${API}/transactions`, transaction);
      alert(`Transaction created! Impact: $${response.data.total_impact_amount.toFixed(2)}`);
      setTransactionAmount("");
      setCustomerName("");
      setShowTransactionForm(false);
      fetchDashboard();
      if (onTransactionCreate) onTransactionCreate(response.data);
    } catch (error) {
      console.error("Error creating transaction:", error);
      alert("Error creating transaction: " + (error.response?.data?.detail || error.message));
    }
  };

  const totalPercentage = Object.values(allocations).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-800">{business.name}</h2>
            <p className="text-gray-600">{business.description}</p>
          </div>
          <button
            onClick={() => setShowTransactionForm(!showTransactionForm)}
            className="bg-green-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-600 transition-all"
          >
            + New Transaction
          </button>
        </div>

        {/* Transaction Form */}
        {showTransactionForm && (
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4">Create New Transaction</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Transaction Amount ($)</label>
                <input
                  type="number"
                  value={transactionAmount}
                  onChange={(e) => setTransactionAmount(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Customer Name (Optional)</label>
                <input
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Customer name"
                />
              </div>
            </div>
            <div className="mt-4 flex gap-4">
              <button
                onClick={createTransaction}
                disabled={!transactionAmount}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Transaction
              </button>
              <button
                onClick={() => setShowTransactionForm(false)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-semibold hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Impact Statistics */}
        {dashboard && (
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-blue-600">${dashboard.total_sales.toFixed(2)}</h3>
              <p className="text-blue-800 font-medium">Total Sales</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-green-600">${dashboard.total_impact.toFixed(2)}</h3>
              <p className="text-green-800 font-medium">Total Impact</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-purple-600">{dashboard.impact_percentage.toFixed(1)}%</h3>
              <p className="text-purple-800 font-medium">Impact Rate</p>
            </div>
          </div>
        )}
      </div>

      {/* Impact Allocation Setup */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">Impact Allocation Setup</h3>
        <p className="text-gray-600 mb-6">
          Choose which social causes you want to support and what percentage of each sale should go to each cause.
        </p>

        <div className="space-y-4 mb-6">
          {causes.map((cause) => (
            <div key={cause.id} className="border border-gray-200 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-800">{cause.name}</h4>
                  <p className="text-gray-600 mb-2">{cause.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="bg-gray-100 px-3 py-1 rounded-full">{cause.category}</span>
                    <span>${cause.cost_per_impact} per {cause.impact_metric}</span>
                  </div>
                </div>
                <div className="ml-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Percentage</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={allocations[cause.id] || ""}
                      onChange={(e) => handleAllocationChange(cause.id, e.target.value)}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <span className="text-gray-500">%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-between items-center">
          <div className="text-lg">
            <span className="text-gray-700">Total Allocation: </span>
            <span className={`font-bold ${totalPercentage > 100 ? 'text-red-600' : 'text-green-600'}`}>
              {totalPercentage.toFixed(1)}%
            </span>
            {totalPercentage > 100 && (
              <span className="text-red-600 text-sm ml-2">Cannot exceed 100%</span>
            )}
          </div>
          <button
            onClick={saveAllocations}
            disabled={totalPercentage > 100}
            className="bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            Save Allocation
          </button>
        </div>
      </div>
    </div>
  );
};

// Business Setup Component
const BusinessSetup = ({ onBusinessCreate }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    industry: "",
    email: "",
    phone: "",
    website: ""
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/businesses`, formData);
      onBusinessCreate(response.data);
    } catch (error) {
      console.error("Error creating business:", error);
      alert("Error creating business: " + (error.response?.data?.detail || error.message));
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Setup Your Business</h2>
        <p className="text-gray-600 mb-8 text-center">
          Let's get your business registered on ImpactLink and start making a difference!
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Business Name *</label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Your Business Name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
            <textarea
              name="description"
              required
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Brief description of your business"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Industry *</label>
              <select
                name="industry"
                required
                value={formData.industry}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Industry</option>
                <option value="Retail">Retail</option>
                <option value="E-commerce">E-commerce</option>
                <option value="Food & Beverage">Food & Beverage</option>
                <option value="Technology">Technology</option>
                <option value="Services">Services</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Education">Education</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="business@example.com"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Website</label>
              <input
                type="url"
                name="website"
                value={formData.website}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://yourwebsite.com"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-4 rounded-lg font-semibold text-lg hover:bg-blue-600 transform hover:scale-105 transition-all shadow-lg"
          >
            Create Business & Start Making Impact
          </button>
        </form>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState("home");
  const [business, setBusiness] = useState(null);
  const [recentTransaction, setRecentTransaction] = useState(null);

  const handleBusinessCreate = (businessData) => {
    setBusiness(businessData);
    setCurrentView("dashboard");
  };

  const handleTransactionCreate = (transactionData) => {
    setRecentTransaction(transactionData);
  };

  const renderContent = () => {
    switch (currentView) {
      case "setup":
        return <BusinessSetup onBusinessCreate={handleBusinessCreate} />;
      case "dashboard":
        return business ? (
          <BusinessDashboard business={business} onTransactionCreate={handleTransactionCreate} />
        ) : (
          <BusinessSetup onBusinessCreate={handleBusinessCreate} />
        );
      default:
        return (
          <>
            <HeroSection />
            <FeaturesSection />
            <div className="py-20 bg-white text-center">
              <div className="max-w-4xl mx-auto px-4">
                <h2 className="text-4xl font-bold text-gray-800 mb-6">Ready to Make an Impact?</h2>
                <p className="text-xl text-gray-600 mb-8">
                  Join thousands of businesses already using ImpactLink to drive positive social change through their sales.
                </p>
                <button
                  onClick={() => setCurrentView("setup")}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-12 py-4 rounded-full font-semibold text-xl hover:from-blue-600 hover:to-purple-700 transform hover:scale-105 transition-all shadow-xl"
                >
                  Get Started Now
                </button>
              </div>
            </div>
          </>
        );
    }
  };

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <div 
              onClick={() => setCurrentView("home")}
              className="flex items-center space-x-2 cursor-pointer"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">I</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">ImpactLink</span>
            </div>
            
            <div className="flex items-center space-x-6">
              <button
                onClick={() => setCurrentView("home")}
                className={`font-medium transition-colors ${currentView === "home" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
              >
                Home
              </button>
              {business && (
                <button
                  onClick={() => setCurrentView("dashboard")}
                  className={`font-medium transition-colors ${currentView === "dashboard" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                >
                  Dashboard
                </button>
              )}
              <button
                onClick={() => setCurrentView("setup")}
                className="bg-blue-500 text-white px-6 py-2 rounded-full font-semibold hover:bg-blue-600 transition-all"
              >
                {business ? "New Business" : "Get Started"}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Recent Transaction Success Alert */}
      {recentTransaction && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4 m-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-700">
                <strong>Transaction Created Successfully!</strong> Impact Amount: ${recentTransaction.total_impact_amount.toFixed(2)}
              </p>
              <button
                onClick={() => setRecentTransaction(null)}
                className="text-green-600 hover:text-green-800 text-sm underline ml-2"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="min-h-screen bg-gray-50">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">I</span>
            </div>
            <span className="text-xl font-bold">ImpactLink</span>
          </div>
          <p className="text-gray-400 mb-4">
            Empowering businesses to drive social change through commerce
          </p>
          <p className="text-gray-500 text-sm">
            © 2025 ImpactLink. Building a better world, one transaction at a time.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;