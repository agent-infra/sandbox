export const frontmatter = {
  pageType: 'custom',
};

import { NoSSR } from '@rspress/core/runtime';
import { useDark } from '@rspress/core/runtime';
import { Suspense, lazy } from 'react';

const ApiReferenceReact = lazy(() =>
  import('@scalar/api-reference-react').then((mod) => ({
    default: mod.ApiReferenceReact,
  })),
);

import '@scalar/api-reference-react/style.css';

const APIPage = () => {
  const dark = useDark();

  return (
    <NoSSR>
      <Suspense fallback={<div>Loading API reference…</div>}>
        <ApiReferenceReact
          key={dark ? 'dark' : 'light'}
          configuration={{
            url: '/v1/openapi.json',
            darkMode: dark,
            forceDarkModeState: dark ? 'dark' : 'light',
            hideTestRequestButton: true,
            hideDownloadButton: true,
            hideDarkModeToggle: true,
            hideClientButton: true,
            hideModels: true,
            telemetry: false,
            documentDownloadType: 'json',
          }}
        />
      </Suspense>
    </NoSSR>
  );
};

export default APIPage;
