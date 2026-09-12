export * from '@rspress/core/theme-original';
export { default as HomeLayout } from './components/HomeLayout';
import { useEffect } from 'react';
import { useI18n } from '@rspress/core/runtime';
import { Layout as DefaultLayout } from '@rspress/core/theme-original';
import { ApiPreferenceProvider, ApiPreferenceSwitch } from './components/ApiPreference';

export { ApiV1, ApiV2, ApiInlineV1, ApiInlineV2, UseV2, useApiPreference } from './components/ApiPreference';
import { getCustomMDXComponent as basicGetCustomMDXComponent } from '@rspress/core/theme-original';
import {
  LlmsContainer,
  LlmsCopyButton,
  LlmsViewOptions,
} from '@rspress/plugin-llms/runtime';

export function HomeFooter() {
  const t = useI18n();
  const message = t('footerMessage');
  if (!message) return null;
  return (
    <footer className="rp-absolute rp-bottom-0 rp-mt-12 rp-py-8 rp-px-6 sm:rp-p-8 rp-w-full rp-border-t rp-border-solid rp-border-divider-light">
      <div className="rp-m-auto rp-w-full rp-text-center">
        <div
          className="rp-font-medium rp-text-sm rp-text-text-2"
          // biome-ignore lint/security/noDangerouslySetInnerHtml: <explanation>
          dangerouslySetInnerHTML={{ __html: message }}
        />
      </div>
    </footer>
  );
}

export function getCustomMDXComponent() {
  const { h1: H1, ...mdxComponents } = basicGetCustomMDXComponent();
  const MyH1 = ({ ...props }) => {
    return (
      <>
        <H1 {...props} />
        <LlmsContainer>
          <LlmsCopyButton />
          <LlmsViewOptions />
        </LlmsContainer>
      </>
    );
  };
  return {
    ...mdxComponents,
    h1: MyH1,
  };
}

// The API reference pages are full-screen viewers; open them in a new tab
// instead of navigating the docs away.
const OPENS_IN_NEW_TAB = /^\/dashboard\/?$|\/daemon\/(api|start\/v1-api)\/?$/;

export function Layout(props: React.ComponentProps<typeof DefaultLayout>) {
  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement | null;
      const anchor = target?.closest?.('a[href]') as HTMLAnchorElement | null;
      if (!anchor || !OPENS_IN_NEW_TAB.test(anchor.getAttribute('href') ?? '')) return;
      event.preventDefault();
      event.stopPropagation();
      window.open(anchor.href, '_blank', 'noopener');
    };
    document.addEventListener('click', onClick, true);
    return () => document.removeEventListener('click', onClick, true);
  }, []);
  return (
    <ApiPreferenceProvider>
      <DefaultLayout {...props} beforeSidebar={<ApiPreferenceSwitch />} />
    </ApiPreferenceProvider>
  );
}
