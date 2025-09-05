package xfkj.fitpro.activity.clockDial.watchTheme1.fragment;
import android.os.Bundle;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import xfkj.fitpro.R;
import xfkj.fitpro.activity.clockDial.watchTheme1.BaseClockDialActivity;
import xfkj.fitpro.adapter.ClockDialListAdapter;
import xfkj.fitpro.base.NewBaseFragment;
import xfkj.fitpro.model.sever.reponse.WatchThemeResponse;
import xfkj.fitpro.view.SpaceItemDecoration;
/**
 * A simple {@link Fragment} subclass.
 */
public class ClockDialTuiJianFragment extends NewBaseFragment {
    RecyclerView mRecyclerView;
    ClockDialListAdapter mAdapter;
    private List<WatchThemeResponse> mWatchThemes;
    public static NewBaseFragment newInstance() {
        return new ClockDialTuiJianFragment();
    }
    @Override
    public int getLayoutId() {
        return R.layout.fragment_clock_dial_tui_jian;
    }
    @Override
    public void initData(Bundle savedInstanceState) {
        if (mWatchThemes == null) {
            mWatchThemes = new ArrayList<>();
        }
        mAdapter = new ClockDialListAdapter(mWatchThemes);
        mRecyclerView.setLayoutManager(new GridLayoutManager(mContext,3));
        mRecyclerView.addItemDecoration(new SpaceItemDecoration(1, 1, 1, 1));
        mRecyclerView.setAdapter(mAdapter);
    }
    @Override
    public void initListener() {
        mAdapter.setOnItemClickListener((view, viewType, data, position) -> {
            WatchThemeResponse theme = (WatchThemeResponse) data;
            ((BaseClockDialActivity)getActivity()).loadDetailsData(theme.getId(),true);
        });
    }
    @Override
    public void setData(Object object) {
        mWatchThemes = (List<WatchThemeResponse>) object;
    }

    @Override
    protected void initViews() {
        super.initViews();
        // 初始化View绑定 - 替换@BindView注解
        mRecyclerView = findViewById(R.id.RecyclerView);
    }
}