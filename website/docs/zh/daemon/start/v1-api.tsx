export const frontmatter = {
  pageType: 'custom',
};

import { useDark, useI18n } from '@rspress/core/runtime';
import { ApiReferenceReact } from '@scalar/api-reference-react';
import { Suspense } from 'react';
import '../api.scss';

import '@scalar/api-reference-react/style.css';

// Same component as the English page — it is locale-aware via useI18n. Kept
// self-contained rather than importing the sibling route page, which rspress
// does not allow one custom page to import from another.
export const APIPage = () => {
  const dark = useDark();
  const t = useI18n();

  return (
    <Suspense
      fallback={
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            height: '60vh',
            gap: '20px',
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '3px solid #f3f3f3',
              borderTop: '3px solid #3498db',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          />
          <div style={{ color: '#666', fontSize: '14px' }}>
            {t('loadingApiReference')}
          </div>
        </div>
      }
    >
      <ApiReferenceReact
        key={dark ? 'dark' : 'light'}
        configuration={{
          baseServerURL: 'http://127.0.0.1:18091',
          url: '/daemon/v1/openapi.json',
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
  );
};

export default APIPage;
