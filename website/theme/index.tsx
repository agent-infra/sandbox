import { getCustomMDXComponent as basicGetCustomMDXComponent } from '@rspress/core/theme';
import {
  LlmsContainer,
  LlmsCopyButton,
  LlmsViewOptions,
} from '@rspress/plugin-llms/runtime';

function getCustomMDXComponent() {
  const { h1: H1, ...mdxComponents } = basicGetCustomMDXComponent();

  const MyH1 = ({ ...props }) => {
    return (
      <>
        <H1 {...props} />
        <LlmsContainer>
          <LlmsCopyButton />
          {/* LlmsViewOptions 组件可根据需要添加  */}
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

export { getCustomMDXComponent };
export * from '@rspress/core/theme';
