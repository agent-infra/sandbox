export * from '@rspress/theme-default';
import { useI18n } from '@rspress/core/runtime';
import {
  getCustomMDXComponent as basicGetCustomMDXComponent,
} from '@rspress/core/theme';
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
    <footer
      className="rp-absolute rp-bottom-0 rp-mt-12 rp-py-8 rp-px-6 sm:rp-p-8 rp-w-full rp-border-t rp-border-solid rp-border-divider-light"
    >
      <div className="rp-m-auto rp-w-full rp-text-center">
        <div
          className="rp-font-medium rp-text-sm rp-text-text-2"
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
