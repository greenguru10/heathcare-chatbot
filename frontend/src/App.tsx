import React, { useState } from 'react';
import { TopNavigation } from './components/TopNavigation';
import { SafetyBanner } from './components/SafetyBanner';
import { PrivacyNoticeModal } from './components/PrivacyNoticeModal';
import { FeedbackModal } from './components/FeedbackModal';
import { ChatPage } from './pages/ChatPage';
import { SourceExplorerPage } from './pages/SourceExplorerPage';
import { AdminPage } from './pages/AdminPage';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'chat' | 'sources'>('chat');
  const [privacyModalOpen, setPrivacyModalOpen] = useState(false);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [activeFeedbackAnswerId, setActiveFeedbackAnswerId] = useState('');

  const handleOpenFeedback = (answerId: string) => {
    setActiveFeedbackAnswerId(answerId);
    setFeedbackModalOpen(true);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-50 text-slate-900 overflow-hidden">
      <SafetyBanner />
      <TopNavigation
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        onOpenPrivacy={() => setPrivacyModalOpen(true)}
      />

      <main className="flex-1 min-h-0 relative overflow-hidden">
        {currentTab === 'chat' && <ChatPage onOpenFeedback={handleOpenFeedback} />}
        {currentTab === 'sources' && (
          <div className="h-full overflow-y-auto">
            <SourceExplorerPage />
          </div>
        )}
      </main>

      <PrivacyNoticeModal
        isOpen={privacyModalOpen}
        onClose={() => setPrivacyModalOpen(false)}
      />

      <FeedbackModal
        isOpen={feedbackModalOpen}
        onClose={() => setFeedbackModalOpen(false)}
        answerId={activeFeedbackAnswerId}
      />
    </div>
  );
};

export default App;
