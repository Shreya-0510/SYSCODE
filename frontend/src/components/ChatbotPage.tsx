import React, { useState } from 'react';
import { Send, Bot, User, Lightbulb } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const ChatbotPage = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI assistant for project cost and timeline analysis. How can I help you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate bot response
    setTimeout(() => {
      const botResponse: Message = {
        id: messages.length + 2,
        text: generateBotResponse(inputMessage),
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);

    setInputMessage('');
  };

  const generateBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('cost') || input.includes('budget')) {
      return "Cost overruns in electrical projects typically occur due to material price volatility, terrain challenges, and regulatory delays. I can help you analyze specific cost factors for your project. What type of project are you working on?";
    } else if (input.includes('delay') || input.includes('timeline')) {
      return "Timeline delays are commonly caused by regulatory approvals, weather conditions, and resource availability. For mountainous terrain projects, expect 20-40% additional time. Would you like me to analyze your specific project timeline?";
    } else if (input.includes('risk')) {
      return "I can help assess project risks across multiple dimensions: financial, operational, environmental, and regulatory. High-risk factors include mountainous terrain, monsoon season construction, and new vendor relationships. What specific risks concern you?";
    } else if (input.includes('terrain')) {
      return "Terrain significantly impacts project costs and timelines:\n• Plains: 1.0x baseline\n• Hilly: 1.2x cost, 20% more time\n• Urban: 1.3x cost due to restrictions\n• Mountainous: 1.4x cost, 40% more time\n\nWhich terrain type are you dealing with?";
    } else {
      return "I can help you with project cost analysis, timeline predictions, risk assessments, and optimization strategies. Try asking me about cost factors, delay causes, risk mitigation, or terrain impacts.";
    }
  };

  const suggestedQuestions = [
    "What factors most impact project costs?",
    "How does terrain affect project timelines?",
    "What are common causes of delays?",
    "How can I reduce project risks?"
  ];

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Project Assistant</h1>
        <p className="text-gray-600">Get instant insights about project costs, timelines, and risk factors</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-[600px] flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                message.sender === 'bot' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
              }`}>
                {message.sender === 'bot' ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
              </div>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white ml-auto'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="text-sm whitespace-pre-line">{message.text}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Suggested Questions */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-2 mb-3">
            <Lightbulb className="h-4 w-4 text-yellow-600" />
            <span className="text-sm font-medium text-gray-700">Suggested Questions:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuestion(question)}
                className="text-sm px-3 py-1 bg-white border border-gray-200 rounded-full hover:bg-gray-50 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask about project costs, timelines, or risks..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;