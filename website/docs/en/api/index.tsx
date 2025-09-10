export const frontmatter = {
  pageType: 'custom',
};

import { RedocStandalone } from 'redoc';

const APIPage = () => {
  return (
    <RedocStandalone
      specUrl="/v1/openapi.json"
      options={{
        hideHostname: true,
        scrollYOffset: () => {
          const header = document.querySelector('.rspress-nav') as HTMLElement;
          return header ? header.offsetHeight : 60;
        },
        untrustedSpec: false,
        nativeScrollbars: true,
        theme: { colors: { primary: { main: '#dd5522' } } },
      }}
    />
  );
};

export default APIPage;
