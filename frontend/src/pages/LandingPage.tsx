import { useEffect } from 'react';
import { useRepositoryStore } from '@/core/store/repository.store';
import { isRepositoryReady, useRepositoriesQuery } from '@/features/repository';
import { Navbar, Hero, FeatureGrid, StatsRow, Footer } from './landing/components';

export default function LandingPage() {
  const activeRepositoryId = useRepositoryStore((s) => s.activeRepositoryId);
  const selectRepository = useRepositoryStore((s) => s.selectRepository);
  const clearRepository = useRepositoryStore((s) => s.clearRepository);
  const listQuery = useRepositoriesQuery();

  const repos = listQuery.data?.repositories ?? [];
  const activeMatch = activeRepositoryId
    ? repos.find((r) => r.id === activeRepositoryId)
    : undefined;

  useEffect(() => {
    if (!listQuery.isSuccess) return;
    if ((listQuery.data?.total ?? 0) === 0) {
      clearRepository();
      return;
    }
    if (activeMatch) {
      selectRepository(activeMatch, { ready: isRepositoryReady(activeMatch.status) });
    }
  }, [listQuery.isSuccess, listQuery.data?.total, activeMatch, clearRepository, selectRepository]);

  return (
    <div className="min-h-screen bg-bg-base">
      <div
        className="fixed inset-0 -z-10"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(232, 160, 69, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(232, 160, 69, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
        }}
      />
      <Navbar />
      <main className="mx-auto flex max-w-[1280px] flex-col items-center px-6 pb-16 pt-20">
        <Hero />
        <div className="mt-20 w-full max-w-4xl">
          <FeatureGrid />
        </div>
        <div className="mt-20">
          <StatsRow />
        </div>
      </main>
      <Footer />
    </div>
  );
}
