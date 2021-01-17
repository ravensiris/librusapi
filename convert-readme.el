(require 'package)
(add-to-list 'package-archives
	     '("melpa" . "https://melpa.org/packages/") t)
(package-initialize)
(unless (package-installed-p 'use-package)
  (package-install 'use-package))
(require 'use-package)

(use-package org
  :ensure t)
(use-package htmlize
  :ensure t)
(use-package ox-rst
  :ensure t)

(switch-to-buffer (find-file "README.org"))
(let ((buffer-file-name (concat (file-name-directory (buffer-file-name)) "README-pypi.org")))
  (org-mode)
  ;; Remove TOC
  (org-narrow-to-element)
  (mark-whole-buffer)
  (call-interactively 'delete-region)
  (widen)
  ;; Remove numbering from export
  (setq org-export-with-section-numbers nil)
  ;; Export
  (call-interactively 'org-rst-export-to-rst)
)
