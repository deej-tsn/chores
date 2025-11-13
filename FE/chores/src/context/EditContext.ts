import { createContext, createElement, useState } from "react";
import type { ReactNode } from "react";

type EditPanelContextType = {
    showEditPanel: number | undefined;
    setEditPanelState: (state: number | undefined) => void;
}

const editPanelContext = createContext<EditPanelContextType>({
    showEditPanel: undefined,
    setEditPanelState: () => {},
});

function EditPanelProvider({ children }: { children: ReactNode }) {
    const [showEditPanel, setEditPanelState] = useState<number | undefined>(undefined);

    return createElement(
        editPanelContext.Provider,
        { value: { showEditPanel, setEditPanelState } },
        children
    );
}

export { editPanelContext, EditPanelProvider };